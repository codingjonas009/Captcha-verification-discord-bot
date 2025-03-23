import discord
import sqlite3
import random
import asyncio
import os
import io
import json
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from discord.ext import commands
from discord import app_commands
from typing import Dict, List, Optional, Tuple


def load_config():
    """Load configuration from JSON file or create a default one if it doesn't exist"""
    config_path = "verify_config.json"

    default_config = {
        "verified_role_id": 1342506397526655046,
        "captcha_settings": {
            "length": 6,
            "width": 280,
            "height": 90,
            "font_size": 40,
            "font_path": "arial.ttf"
        },
        "verification_settings": {
            "max_attempts": 5,
            "timeout_minutes": 10,
            "db_filename": "captcha_verification.db"
        },
        "messages": {
            "welcome": "Welcome to the server. Please complete the captcha verification process to gain access.",
            "already_verified": "Your account has already been verified on this server.",
            "verification_success": "Verification completed successfully. You now have full access to the server.",
            "verification_failed": "The captcha entry was incorrect. Please attempt verification again.",
            "verification_timeout": "Maximum verification attempts exceeded. Please try again after the timeout period."
        }
    }

    # Check if config file exists
    if not os.path.exists(config_path):
        # Create default config file
        with open(config_path, 'w') as config_file:
            json.dump(default_config, config_file, indent=4)
        print(f"Created default configuration file at {config_path}")
        return default_config

    # Load existing config
    try:
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
        print(f"Loaded configuration from {config_path}")
        return config
    except Exception as e:
        print(f"Error loading config: {e}")
        print("Using default configuration")
        return default_config


class CaptchaVerification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = load_config()
        self.active_captchas: Dict[int, str] = {}
        self.user_attempts: Dict[int, int] = {}
        self.timeouts: Dict[int, float] = {}

        self._init_db()

        os.makedirs("fonts", exist_ok=True)

        try:
            font_path = self.config["captcha_settings"]["font_path"]
            if not os.path.exists(font_path):
                system_fonts = [
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
                    "/System/Library/Fonts/Helvetica.ttc",  # MacOS
                    "C:\\Windows\\Fonts\\Arial.ttf",  # Windows
                    "arial.ttf",  # Fallback
                ]

                for font_path in system_fonts:
                    if os.path.exists(font_path):
                        self.config["captcha_settings"]["font_path"] = font_path
                        # Save the updated config
                        with open("verify_config.json", 'w') as config_file:
                            json.dump(self.config, config_file, indent=4)
                        break
        except Exception as e:
            print(f"Font initialization error: {e}")

    def _init_db(self):
        db_filename = self.config["verification_settings"]["db_filename"]
        conn = sqlite3.connect(db_filename)
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS verified_users (
            user_id INTEGER PRIMARY KEY,
            guild_id INTEGER,
            verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS active_buttons (
            button_id TEXT PRIMARY KEY,
            message_id INTEGER,
            channel_id INTEGER,
            guild_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        conn.commit()
        conn.close()

    async def handle_verification_button(self, interaction: discord.Interaction):
        """Handle clicks on the verification button"""
        user_id = interaction.user.id
        guild_id = interaction.guild.id

        # Check if user is already verified
        if self.is_verified(user_id, guild_id):
            already_verified_embed = discord.Embed(
                title="✅ Verification Status",
                description=self.config["messages"]["already_verified"],
                color=discord.Color.green()
            )

            await interaction.response.send_message(
                embed=already_verified_embed,
                ephemeral=True
            )
            return

        # Check if user is in timeout
        if user_id in self.timeouts:
            timeout_end = self.timeouts[user_id]
            current_time = asyncio.get_event_loop().time()

            if current_time < timeout_end:
                remaining = int(timeout_end - current_time)
                minutes = remaining // 60
                seconds = remaining % 60

                await interaction.response.send_message(
                    f"A timeout is currently in effect. Please attempt verification again in {minutes}m {seconds}s.",
                    ephemeral=True
                )
                return
            else:
                del self.timeouts[user_id]

        # Generate a captcha
        captcha_file, solution = await self.create_captcha()
        self.active_captchas[user_id] = solution

        captcha_embed = discord.Embed(
            title="🔒 Verification Required",
            description="Please complete the captcha verification below",
            color=discord.Color.blue()
        )
        captcha_embed.set_image(url="attachment://captcha.png")

        captcha_view = self.CaptchaView(
            self,
            solution,
            user_id,
            guild_id
        )

        await interaction.response.send_message(
            embed=captcha_embed,
            file=captcha_file,
            view=captcha_view,
            ephemeral=True
        )

    def is_verified(self, user_id: int, guild_id: int) -> bool:
        db_filename = self.config["verification_settings"]["db_filename"]
        conn = sqlite3.connect(db_filename)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT 1 FROM verified_users WHERE user_id = ? AND guild_id = ?",
            (user_id, guild_id)
        )

        result = cursor.fetchone() is not None
        conn.close()

        return result

    def mark_as_verified(self, user_id: int, guild_id: int):
        db_filename = self.config["verification_settings"]["db_filename"]
        conn = sqlite3.connect(db_filename)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT OR REPLACE INTO verified_users (user_id, guild_id) VALUES (?, ?)",
            (user_id, guild_id)
        )

        conn.commit()
        conn.close()

    def store_button(self, button_id: str, message_id: int, channel_id: int, guild_id: int):
        db_filename = self.config["verification_settings"]["db_filename"]
        conn = sqlite3.connect(db_filename)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO active_buttons (button_id, message_id, channel_id, guild_id) VALUES (?, ?, ?, ?)",
            (button_id, message_id, channel_id, guild_id)
        )

        conn.commit()
        conn.close()

    def remove_button(self, button_id: str):
        db_filename = self.config["verification_settings"]["db_filename"]
        conn = sqlite3.connect(db_filename)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM active_buttons WHERE button_id = ?", (button_id,))

        conn.commit()
        conn.close()

    def generate_captcha_text(self) -> str:
        """Generate random captcha text"""
        uppercase_letters = "ABCDEFGHJKLMNPQRSTUVWXYZ"
        digits = "23456789"

        characters = uppercase_letters + digits
        captcha_length = self.config["captcha_settings"]["length"]
        captcha_text = ''.join(random.choice(characters) for _ in range(captcha_length))

        return captcha_text

    def generate_captcha_image(self, text: str) -> io.BytesIO:
        """Generate a captcha image with the given text"""
        width = self.config["captcha_settings"]["width"]
        height = self.config["captcha_settings"]["height"]

        image = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype(self.config["captcha_settings"]["font_path"],
                                      self.config["captcha_settings"]["font_size"])
        except Exception as e:
            print(f"Error loading font: {e}")
            font = ImageFont.load_default()

        text_bbox = draw.textbbox((0, 0), text, font=font) if hasattr(draw, 'textbbox') else font.getbbox(text)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = (width - text_width) // 2
        text_y = (height - text_height) // 2

        for _ in range(width * height // 20):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            draw.point((x, y), fill=(random.randint(0, 200), random.randint(0, 200), random.randint(0, 200)))

        for _ in range(8):
            x1 = random.randint(0, width - 1)
            y1 = random.randint(0, height - 1)
            x2 = random.randint(0, width - 1)
            y2 = random.randint(0, height - 1)
            draw.line([(x1, y1), (x2, y2)],
                      fill=(random.randint(0, 200), random.randint(0, 200), random.randint(0, 200)), width=1)

        for i, char in enumerate(text):
            char_x = text_x + i * (text_width // len(text))
            char_y = text_y + random.randint(-10, 10)

            char_img = Image.new('RGBA', (text_width // len(text) + 10, text_height + 20), (255, 255, 255, 0))
            char_draw = ImageDraw.Draw(char_img)
            char_draw.text((5, 10), char, font=font, fill=(0, 0, 0))

            rotation = random.uniform(-25, 25)
            char_img = char_img.rotate(rotation, expand=True, fillcolor=(255, 255, 255, 0), resample=Image.BICUBIC)

            image.paste(char_img, (char_x, char_y), char_img)

        image = image.filter(ImageFilter.GaussianBlur(radius=0.5))

        byte_array = io.BytesIO()
        image.save(byte_array, format='PNG')
        byte_array.seek(0)

        return byte_array

    async def create_captcha(self) -> Tuple[discord.File, str]:
        # Generate random captcha text
        captcha_text = self.generate_captcha_text()

        # Generate captcha image
        captcha_image = self.generate_captcha_image(captcha_text)

        # Create Discord file
        captcha_file = discord.File(captcha_image, filename="captcha.png")

        return captcha_file, captcha_text

    class CaptchaModal(discord.ui.Modal):
        def __init__(self, cog, solution: str, user_id: int, guild_id: int):
            super().__init__(title="Captcha Verification")
            self.cog = cog
            self.solution = solution
            self.user_id = user_id
            self.guild_id = guild_id

            self.answer = discord.ui.TextInput(
                label="Enter the text from the captcha",
                placeholder="Please enter the captcha text...",
                required=True,
                max_length=10
            )
            self.add_item(self.answer)

        async def on_submit(self, interaction: discord.Interaction):
            if self.answer.value.strip().upper() == self.solution.strip().upper():
                guild = interaction.guild
                role = guild.get_role(self.cog.config["verified_role_id"])

                if role:
                    try:
                        await interaction.user.add_roles(role)
                        self.cog.mark_as_verified(self.user_id, self.guild_id)

                        success_embed = discord.Embed(
                            title="✅ Verification Successful",
                            description=self.cog.config["messages"]["verification_success"],
                            color=discord.Color.green()
                        )

                        await interaction.response.edit_message(
                            embed=success_embed,
                            view=None,
                            attachments=[]
                        )

                        if self.user_id in self.cog.active_captchas:
                            del self.cog.active_captchas[self.user_id]
                        if self.user_id in self.cog.user_attempts:
                            del self.cog.user_attempts[self.user_id]

                    except discord.Forbidden:
                        await interaction.response.send_message(
                            "Insufficient permissions to assign roles. Please contact an administrator for assistance.",
                            ephemeral=True
                        )
                else:
                    await interaction.response.send_message(
                        "Verification role not found in configuration. Please contact an administrator for assistance.",
                        ephemeral=True
                    )
            else:
                if self.user_id not in self.cog.user_attempts:
                    self.cog.user_attempts[self.user_id] = 1
                else:
                    self.cog.user_attempts[self.user_id] += 1

                attempts = self.cog.user_attempts[self.user_id]

                if attempts >= self.cog.config["verification_settings"]["max_attempts"]:
                    timeout_end = asyncio.get_event_loop().time() + (
                                self.cog.config["verification_settings"]["timeout_minutes"] * 60)
                    self.cog.timeouts[self.user_id] = timeout_end

                    timeout_embed = discord.Embed(
                        title="⛔ Verification Limit Reached",
                        description=self.cog.config["messages"]["verification_timeout"],
                        color=discord.Color.red()
                    )
                    timeout_embed.add_field(
                        name="Timeout Period",
                        value=f"You may attempt verification again in {self.cog.config['verification_settings']['timeout_minutes']} minutes."
                    )

                    await interaction.response.edit_message(
                        embed=timeout_embed,
                        view=None,
                        attachments=[]
                    )

                    await asyncio.sleep(self.cog.config["verification_settings"]["timeout_minutes"] * 60)
                    if self.user_id in self.cog.user_attempts:
                        del self.cog.user_attempts[self.user_id]
                    if self.user_id in self.cog.timeouts:
                        del self.cog.timeouts[self.user_id]
                else:
                    new_captcha_file, new_solution = await self.cog.create_captcha()
                    self.cog.active_captchas[self.user_id] = new_solution

                    failed_embed = discord.Embed(
                        title="❌ Verification Unsuccessful",
                        description=self.cog.config["messages"]["verification_failed"],
                        color=discord.Color.red()
                    )
                    failed_embed.add_field(
                        name="Attempts",
                        value=f"{attempts}/{self.cog.config['verification_settings']['max_attempts']}"
                    )
                    failed_embed.set_image(url="attachment://captcha.png")

                    view = CaptchaVerification.CaptchaView(
                        self.cog,
                        new_solution,
                        self.user_id,
                        self.guild_id
                    )

                    await interaction.response.edit_message(
                        embed=failed_embed,
                        view=view,
                        attachments=[new_captcha_file]
                    )

    class CaptchaView(discord.ui.View):
        def __init__(self, cog, solution: str, user_id: int, guild_id: int):
            super().__init__(timeout=None)
            self.cog = cog
            self.solution = solution
            self.user_id = user_id
            self.guild_id = guild_id

            self.button_id = f"captcha_{user_id}_{random.randint(1000, 9999)}"
        custom_emoji = "<:captcha:1353308565061767259>"
        @discord.ui.button(label="Enter Captcha",emoji=custom_emoji , style=discord.ButtonStyle.primary, custom_id="captcha_button")
        async def captcha_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            if self.user_id in self.cog.timeouts:
                timeout_end = self.cog.timeouts[self.user_id]
                current_time = asyncio.get_event_loop().time()

                if current_time < timeout_end:
                    remaining = int(timeout_end - current_time)
                    minutes = remaining // 60
                    seconds = remaining % 60

                    await interaction.response.send_message(
                        f"A timeout period is currently active. Please attempt verification again in {minutes}m {seconds}s.",
                        ephemeral=True
                    )
                    return
                else:
                    del self.cog.timeouts[self.user_id]

            # Open the modal
            modal = CaptchaVerification.CaptchaModal(
                self.cog,
                self.solution,
                self.user_id,
                self.guild_id
            )

            await interaction.response.send_modal(modal)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup_verification(self, ctx):
        embed = discord.Embed(
            title="🔒 Server Verification System",
            description="""
**Welcome to our server.**

To maintain the security and integrity of our community, we require all new members to complete a brief verification process. Please follow these instructions:

1. **Click the "Verify" button** below to initiate the verification procedure.
2. You will be presented with a **Captcha challenge**. Complete this verification step to confirm your identity.
3. Upon successful verification, you will gain complete access to the server.

Thank you for your cooperation in helping us maintain a secure environment for all members.

---

This message can be customized to better suit your community's requirements.
            """,
            color=discord.Color.blue()
        )

        embed.set_footer(

            text=f"┃ Captcha Verification",
            icon_url="https://cdn.discordapp.com/attachments/1351096159510204456/1353315601682272276/lock.png?ex=67e134de&is=67dfe35e&hm=58e86acf0ceb66f2a8f986f4d02c6a740c4232b60847df8dbf3def4434e1f782&",
        )

        class VerificationView(discord.ui.View):
            def __init__(self, cog):
                super().__init__(timeout=None)
                self.cog = cog

                self.button_id = f"verify_{random.randint(1000, 9999)}"

            custom_emoji = "<:verify:1353299720373669939>"
            @discord.ui.button(label="Verify", style=discord.ButtonStyle.green, emoji=custom_emoji, custom_id="verify_button")
            async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                user_id = interaction.user.id
                guild_id = interaction.guild.id

                if self.cog.is_verified(user_id, guild_id):
                    already_verified_embed = discord.Embed(
                        title="✅ Verification Status",
                        description=self.cog.config["messages"]["already_verified"],
                        color=discord.Color.green()
                    )

                    await interaction.response.send_message(
                        embed=already_verified_embed,
                        ephemeral=True
                    )
                    return

                if user_id in self.cog.timeouts:
                    timeout_end = self.cog.timeouts[user_id]
                    current_time = asyncio.get_event_loop().time()

                    if current_time < timeout_end:
                        remaining = int(timeout_end - current_time)
                        minutes = remaining // 60
                        seconds = remaining % 60

                        await interaction.response.send_message(
                            f"A timeout period is currently active. Please attempt verification again in {minutes}m {seconds}s.",
                            ephemeral=True
                        )
                        return
                    else:
                        del self.cog.timeouts[user_id]

                captcha_file, solution = await self.cog.create_captcha()
                self.cog.active_captchas[user_id] = solution

                captcha_embed = discord.Embed(
                    title="🔒 Verification Required",
                    description="Please complete the captcha verification below",
                    color=discord.Color.blue()
                )
                captcha_embed.set_image(url="attachment://captcha.png")

                captcha_view = CaptchaVerification.CaptchaView(
                    self.cog,
                    solution,
                    user_id,
                    guild_id
                )

                await interaction.response.send_message(
                    embed=captcha_embed,
                    file=captcha_file,
                    view=captcha_view,
                    ephemeral=True
                )

        view = VerificationView(self)
        message = await ctx.send(embed=embed, view=view)

        self.store_button(
            view.button_id,
            message.id,
            ctx.channel.id,
            ctx.guild.id
        )

        await ctx.message.delete()

    @commands.Cog.listener()
    async def on_ready(self):
        """Load all active buttons from the database when the bot starts"""
        print(f"{self.__class__.__name__} cog is ready!")

        db_filename = self.config["verification_settings"]["db_filename"]
        conn = sqlite3.connect(db_filename)
        cursor = conn.cursor()

        cursor.execute("SELECT button_id, message_id, channel_id, guild_id FROM active_buttons")
        buttons = cursor.fetchall()

        conn.close()

        print(f"Loading {len(buttons)} verification buttons...")

        for button_id, message_id, channel_id, guild_id in buttons:
            try:
                channel = self.bot.get_channel(channel_id)
                if not channel:
                    channel = await self.bot.fetch_channel(channel_id)

                if channel:
                    try:
                        message = await channel.fetch_message(message_id)

                        if "verify_" in button_id:
                            class PersistentVerificationView(discord.ui.View):
                                def __init__(self, cog):
                                    super().__init__(timeout=None)
                                    self.cog = cog

                                custom_emoji = "<:verify:1353299720373669939>"
                                @discord.ui.button(label="Verify", style=discord.ButtonStyle.green, emoji=custom_emoji,
                                                   custom_id="verify_button")
                                async def verify_button(self, interaction: discord.Interaction,
                                                        button: discord.ui.Button):
                                    await self.cog.handle_verification_button(interaction)

                            self.bot.add_view(PersistentVerificationView(self))

                    except discord.NotFound:
                        self.remove_button(button_id)

                    except Exception as e:
                        print(f"Error loading button {button_id}: {e}")

            except Exception as e:
                print(f"Error processing button {button_id}: {e}")


class VerificationView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

        self.button_id = f"verify_{random.randint(1000, 9999)}"

    custom_emoji = "<:verify:1353299720373669939>"
    @discord.ui.button(label="Verify", style=discord.ButtonStyle.green, emoji=custom_emoji, custom_id="verify_button")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        guild_id = interaction.guild.id

        if self.cog.is_verified(user_id, guild_id):
            already_verified_embed = discord.Embed(
                title="✅ Verification Status",
                description=self.cog.config["messages"]["already_verified"],
                color=discord.Color.green()
            )

            await interaction.response.send_message(
                embed=already_verified_embed,
                ephemeral=True
            )
            return

        if user_id in self.cog.timeouts:
            timeout_end = self.cog.timeouts[user_id]
            current_time = asyncio.get_event_loop().time()

            if current_time < timeout_end:
                remaining = int(timeout_end - current_time)
                minutes = remaining // 60
                seconds = remaining % 60

                await interaction.response.send_message(
                    f"A timeout period is currently active. Please attempt verification again in {minutes}m {seconds}s.",
                    ephemeral=True
                )
                return
            else:
                del self.cog.timeouts[user_id]

        captcha_file, solution = await self.cog.create_captcha()
        self.cog.active_captchas[user_id] = solution

        captcha_embed = discord.Embed(
            title="🔒 Verification Required",
            description="Please complete the captcha verification below",
            color=discord.Color.blue()
        )
        captcha_embed.set_image(url="attachment://captcha.png")

        captcha_view = CaptchaVerification.CaptchaView(
            self.cog,
            solution,
            user_id,
            guild_id
        )

        await interaction.response.send_message(
            embed=captcha_embed,
            file=captcha_file,
            view=captcha_view,
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(CaptchaVerification(bot))
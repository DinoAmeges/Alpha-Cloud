import discord
from discord.ext import commands
import json
from discord.ui import View, Select, Modal, TextInput

# Cargar configuración
with open("config/config.json") as f:
    config = json.load(f)

# Configuración de Intents y el bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

import discord
from discord.ext import commands
from discord.ui import View, Select

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Diccionario de preguntas por categoría
ticket_questions = {
    "Soporte": [
        "¿Cuál es tu problema o pregunta?",
        "¿Desde cuándo ocurre este problema?",
        "¿Has intentado solucionarlo? ¿Cómo?"
    ],
    "Apelacion": [
        "¿Cuál fue la sanción que recibiste?",
        "¿Quién te sancionó y cuándo?",
        "¿Por qué crees que fue injusta la sanción?"
    ],
    "Reportar Usuario": [
        "¿A quién estás reportando? (menciona su usuario)",
        "¿Qué hizo esta persona?",
        "¿Tienes pruebas del comportamiento? (links o imágenes)"
    ],
    "Compras": [
        "¿Qué producto o servicio compraste?",
        "¿Cuál es tu problema con la compra?",
        "¿Tienes alguna captura o recibo de pago?"
    ],
    "Bug": [
        "¿Qué error encontraste?",
        "¿Cómo lo descubriste?",
        "¿Se puede replicar fácilmente? Explica cómo."
    ],
    "Sugerencia": [
        "¿Cuál es tu sugerencia?",
        "¿Por qué crees que sería útil para la comunidad?",
        "¿Ya ha sido discutida antes? ¿Dónde?"
    ],
    "Alianza": [
        "¿Cuál es el nombre de tu servidor/clan?",
        "¿Cuál es la propuesta de alianza?",
        "¿Por qué te gustaría aliarte con nosotros?"
    ],
    "VPS": [
        "¿Qué tipo de VPS adquiriste o deseas adquirir?",
        "¿Presentas fallos de conexión o rendimiento?",
        "¿Tienes alguna captura o evidencia del error?"
    ],
    "Dominio": [
        "¿Qué dominio compraste o deseas adquirir?",
        "¿Tu dominio ya fue configurado correctamente?",
        "¿Tienes comprobante del pago o registro?"
    ],
    "IP Dedicada": [
        "¿Estás solicitando o tienes una IP dedicada?",
        "¿Presentas algún problema con tu IP?",
        "¿En qué servicio estás usando la IP?"
    ],
    "Facturación": [
        "¿Tienes dudas sobre un cobro?",
        "¿Cuál es tu número de orden?",
        "¿Deseas reembolso, aclaración o cambio?"
    ],
    "Configuración": [
        "¿Qué servicio deseas configurar?",
        "¿Qué sistema operativo estás utilizando?",
        "¿Tienes acceso administrativo?"
    ],
    "Rendimiento": [
        "¿Qué problema de rendimiento experimentas?",
        "¿Con qué frecuencia ocurre?",
        "¿Qué servicios están afectados?"
    ],
    "Seguridad": [
        "¿Cuál es el problema de seguridad que detectaste?",
        "¿Hay logs o evidencia del incidente?",
        "¿Cuándo ocurrió?"
    ],
    
}

class TicketModal(Modal):
    def __init__(self, ticket_type):
        super().__init__(title=f"Formulario de {ticket_type}")
        self.ticket_type = ticket_type
        self.responses = []

        for i, question in enumerate(ticket_questions[ticket_type]):
            self.add_item(TextInput(label=question, custom_id=str(i), required=True))

    async def on_submit(self, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.guild

        for i in range(len(self.children)):
            self.responses.append(self.children[i].value)

        # Crear canal
        category = discord.utils.get(guild.categories, name="Soporte")
        if category is None:
            category = await guild.create_category("Soporte")

        channel_name = f"{self.ticket_type.lower()}-{user.name}".replace(" ", "-")
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        ticket_channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites,
            reason=f"Nuevo ticket de tipo {self.ticket_type}"
        )

        # Crear embed con respuestas
        embed = discord.Embed(
            title=f"🎫 Ticket de {self.ticket_type} | {user.name}",
            color=discord.Color.blurple()
        )
        for question, answer in zip(ticket_questions[self.ticket_type], self.responses):
            embed.add_field(name=f"❓ {question}", value=answer, inline=False)

        embed.set_footer(text=f"ID de usuario: {user.id}")
        embed.set_thumbnail(url=user.display_avatar.url)

        await ticket_channel.send(embed=embed)
        await interaction.response.send_message(f"✅ Tu ticket ha sido creado en {ticket_channel.mention}", ephemeral=True)

class TicketDropdown(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=label, emoji=emoji)
            for label, emoji in [
                ("Soporte", "⚙️"),
                ("Apelacion", "⚖️"),
                ("Reportar Usuario", "🛑"),
                ("Compras", "🏷️"),
                ("Bug", "🪲"),
                ("Sugerencia", "🧠"),
                ("Virtual Machine", "🖥️"),
                ("Dominios", "🌐"),
                ("Hosting", "🏠"),
                ("Facturación", "💳"),
            ]
        ]
        super().__init__(placeholder="Selecciona el tipo de ticket", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(TicketModal(self.values[0]))

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketDropdown())

@bot.command()
async def tickets(ctx):
    embed = discord.Embed(
        title="🎫 Alpha Cloud Services | Sistema de Tickets",
        description=(
            "Selecciona el tipo de asistencia que necesitas en el menú desplegable a continuación.\n\n"
            "**Categorías Disponibles:**\n"
            "⚙️ Soporte\n"
            "⚖️ Apelación\n"
            "🛑 Reportar Usuario\n"
            "🏷️ Compras\n"
            "🪲 Bug\n"
            "🖥️ Virtual Machine\n"
            "🌐 Dominios\n"
            "🏠 Hosting\n"
            "💳 Facturación\n"
            "🧠 Sugerencia\n\n"
            "⚠️ No abuses del sistema de tickets o podrías ser sancionado."
        ),
        color=discord.Color.blue()
    )
    embed.set_image(url="https://media.discordapp.net/attachments/1360652083640012839/1360714274019741926/standard.gif?ex=67fc1f6b&is=67facdeb&hm=c10f53178862105eb63b3c276b1b9beb2d87a1395820093698b5b7a3507f4ae0&=&width=750&height=300")
    embed.set_footer(text="Sistema de Tickets - Alpha Cloud Services")

    await ctx.send(embed=embed, view=TicketView())
    

import discord
from discord.ext import commands

# Cog de bienvenida
class Bienvenida(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Crear el embed con la bienvenida
        embed = discord.Embed(
            title="🎉 ¡Bienvenido a Alpha Cloud 2025! 🎉",
            description=f"Hola {member.mention}, ¡estás a punto de empezar tu aventura en Alpha Cloud!\n\n"
                        "Eres el jugador número **{0}**. ¡Estamos muy emocionados de tenerte aquí!".format(member.guild.member_count),
            color=discord.Color.green()
        )
        
        # Agregar la imagen del perfil del usuario
        embed.set_thumbnail(url=member.avatar.url)
        
        # Agregar el footer con el nombre del sistema
        embed.set_footer(text="Sistema de Bienvenida Alpha Cloud")
        
        # Buscar el canal de bienvenida+
        channel = discord.utils.get(member.guild.text_channels, name="bienvenida+")
        if channel:
            try:
                # Intentar enviar el mensaje de bienvenida
                await channel.send(embed=embed)
                print(f"Mensaje enviado al canal {channel.name}")  # Mensaje de depuración
            except discord.DiscordException as e:
                print(f"No se pudo enviar el mensaje al canal {channel.name}: {e}")  # Manejo de errores
        else:
            print("Canal 'bienvenida+' no encontrado. Buscando canal de bienvenida predeterminado...")  # Mensaje de depuración
            # Si no se encuentra el canal 'bienvenida+', buscar un canal predeterminado 'bienvenida'
            default_channel = discord.utils.get(member.guild.text_channels, name="bienvenida")
            if default_channel:
                try:
                    await default_channel.send(embed=embed)
                    print(f"Mensaje enviado al canal {default_channel.name}")  # Mensaje de depuración
                except discord.DiscordException as e:
                    print(f"No se pudo enviar el mensaje al canal {default_channel.name}: {e}")  # Manejo de errores
            else:
                print("No se encontró ningún canal de bienvenida. Asegúrate de que el canal exista.")  # Mensaje de depuración

# Cargar el cog en tu bot
def setup(bot):
    bot.add_cog(Bienvenida(bot))


# Cog de verificación
class Verificacion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="verificacion")
    async def verificacion(self, ctx):
        # Crear el embed con los términos y condiciones
        embed = discord.Embed(
            title="📝 **Términos y Condiciones | Alpha Cloud 2025**",
            description="**¡Bienvenido!** Por favor, lee y acepta los siguientes términos y condiciones para poder continuar.\n\n"
                        "Al hacer clic en **Aceptar**, confirmas que estás de acuerdo con estos términos.",
            color=discord.Color.blue()
        )
        embed.set_footer(text="Si tienes alguna duda, contacta con el equipo de soporte.")
        embed.set_thumbnail(url=ctx.guild.icon.url)  # Usar el ícono del servidor como miniatura

        embed.add_field(
            name="📜 **Términos a seguir**\n\n",
            value="1️⃣ Respetar a los demás usuarios.\n"
                  "2️⃣ No compartir contenido inapropiado.\n"
                  "3️⃣ Seguir las reglas del servidor.\n"
                  "4️⃣ Ser amable y colaborativo.",
            inline=False
        )

        embed.add_field(
            name="🔒 **Privacidad y Seguridad**\n\n",
            value="✅ Tu información está protegida.\n"
                  "❌ No compartas información personal en el servidor.",
            inline=False
        )

        embed.add_field(
            name="💬 **¿Tienes dudas?**",
            value=(
                "Si tienes alguna duda sobre los términos, por favor, no dudes en preguntar a los administradores.\n\n"
                "Atentamente,\n\n"
                "Ameges (Gerente Ejecutivo Alpha Cloud @ 2025)"
            )
        )

        # Crear el botón para aceptar
        button = discord.ui.Button(label="✅ Aceptar Términos", style=discord.ButtonStyle.green)

        # Función que se ejecuta cuando se presiona el botón
        async def button_callback(interaction):
            # Verificar si el usuario ya tiene el rol
            role = discord.utils.get(ctx.guild.roles, name="Verificado")
            if role:
                # Comprobar si el usuario ya tiene el rol
                if role in interaction.user.roles:
                    await interaction.response.send_message("Ya estás verificado. 🎉", ephemeral=True)
                else:
                    # Agregar el rol de "Verificado"
                    await interaction.user.add_roles(role)
                    await interaction.response.send_message("¡Verificación completa! Has aceptado los términos y condiciones y se te ha dado el rol de Verificado. 🎉", ephemeral=True)
            else:
                await interaction.response.send_message("El rol 'Verificado' no se encuentra en el servidor. Por favor, contacta a un administrador. ⚠️", ephemeral=True)

        # Asignar la función al botón
        button.callback = button_callback

        # Crear una vista que contiene el botón
        view = discord.ui.View()
        view.add_item(button)

        # Enviar el mensaje con el embed y el botón al canal donde se ejecutó el comando
        await ctx.send(embed=embed, view=view)

# Cog de pagos
class Pagos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="pago")
    async def pago(self, ctx, monto: int):
        user_id = ctx.author.id
        # Aquí iría la lógica para registrar el pago en la base de datos, por ejemplo:
        # await registrar_pago(user_id, monto)
        
        # Simulando un mensaje de confirmación
        await ctx.send(f"💰 Pago de {monto} procesado con éxito. ¡Gracias por tu pago! 🎉")

# Cog de estadísticas
class Estadisticas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="estadisticas")
    async def estadisticas(self, ctx):
        # Ejemplo de comando que muestra estadísticas
        await ctx.send("📊 Este es un comando de estadísticas.")

# Cog de idiomas
class Idiomas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.idiomas = {
            "es": {
                "payment_success": "¡Pago exitoso! 💵"
            },
            "en": {
                "payment_success": "Payment successful! 💸"
            }
        }

    @commands.command(name="idioma")
    async def idioma(self, ctx, lang: str):
        """Comando para cambiar el idioma del bot."""
        if lang in self.idiomas:
            # Guardar el idioma preferido en la base de datos
            # await set_idioma_in_db(ctx.author.id, lang)
            await ctx.send(f"🌍 Idioma cambiado a {lang}.")
        else:
            await ctx.send("🌐 Idioma no reconocido.")

# Evento al iniciar el bot
@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    await bot.tree.sync()  # Sincronización de los comandos de barra (Slash commands)

    # Cargar las cogs (extensiones) directamente con await
    try:
        await bot.add_cog(Verificacion(bot))
        await bot.add_cog(Pagos(bot))
        await bot.add_cog(Estadisticas(bot))
        await bot.add_cog(Idiomas(bot))
        print("🔹 Cogs cargadas correctamente.")
    except Exception as e:
        print(f"❌ Error al cargar las cogs: {e}")

# Iniciar el bot
bot.run(config["token"])

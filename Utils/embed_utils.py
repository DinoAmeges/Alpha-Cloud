# utils/embed_utils.py

import discord

def crear_embed_bienvenida(idioma_data, miembro):
    embed = discord.Embed(
        title=idioma_data["welcome"],
        description=f"{idioma_data['desc']} {miembro.mention}",
        color=discord.Color.blue()
    )
    return embed

def crear_embed_ticket(idioma_data, respuestas, autor):
    embed = discord.Embed(
        title="🎫 Nuevo Ticket de Soporte",
        color=discord.Color.green()
    )
    embed.add_field(name="👤 Usuario", value=f"{autor.name}#{autor.discriminator}", inline=False)

    for pregunta, respuesta in respuestas.items():
        embed.add_field(name=f"❓ {pregunta}", value=respuesta or "Sin respuesta", inline=False)

    embed.set_footer(text="Sistema de Tickets | Alpha Cloud")
    return embed

def crear_embed_contacto(idioma_data):
    embed = discord.Embed(
        title="📞 Contacto",
        description=idioma_data["contact"],
        color=discord.Color.purple()
    )
    return embed

def crear_embed_soporte(idioma_data):
    embed = discord.Embed(
        title="🆘 Soporte",
        description=idioma_data["soporte"],
        color=discord.Color.orange()
    )
    return embed

def crear_embed_estadisticas(idioma_data, total_users, total_servers):
    embed = discord.Embed(
        title=idioma_data["stats_dm"],
        color=discord.Color.teal()
    )
    embed.add_field(name="👥 Usuarios", value=str(total_users))
    embed.add_field(name="🛡️ Servidores", value=str(total_servers))
    return embed

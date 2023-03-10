from datetime import datetime, timedelta
from typing import Literal, Optional, Union

import discord
from discord import app_commands
from discord.ext import commands


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ban", description="Ban someone")
    @discord.app_commands.describe(member="The member you want to ban")
    @discord.app_commands.describe(reason="Why do you want to ban this member?")
    async def ban(self, interaction: discord.Interaction, member: discord.Member, *, reason: str = None):
        try:
            # Check if the bot has the permission to ban members
            if not interaction.guild.me.guild_permissions.ban_members:
                embed = discord.Embed(title="Permission Denied", color=0xff0000)
                embed.add_field(name="Error", value="I do not have permission to ban members.", inline=True)
                return await interaction.response.send_message(embed=embed, ephemeral=True)

            # Check if the user has the permission to ban members
            if not interaction.user.guild_permissions.ban_members:
                embed = discord.Embed(title="Permission Denied", color=0xff0000)
                embed.add_field(name="Error", value="You do not have permission to use this command.", inline=True)
                return await interaction.response.send_message(embed=embed, ephemeral=True)

            if reason is None:
                reason = "No reason provided"

            # Send a DM to the banned member
            try:
                embed = discord.Embed(title=f"You have been banned from **{interaction.guild.name}**!", color=0x00D9FF,)
                embed.add_field(name="Banned by", value=interaction.user.mention)
                embed.add_field(name="Reason", value=reason)
                await member.send(embed=embed)
            except Exception as e:
                print(f"Failed to DM {member}: {e}")


            embed = discord.Embed(title=" Member has been banned", color=0x00D9FF)
            embed.add_field(name="Banned User", value=member.mention)
            embed.add_field(name="Banned by", value=interaction.user.mention)
            embed.add_field(name="Reason", value=reason)
            await interaction.response.send_message(embed=embed)

            # Ban the member and provide the reason and the user who banned them
            try:
                await member.ban(reason=f"{reason} | Banned by: {interaction.user}")
            except Exception as e:
                print(f"Failed to ban {member}: {e}")
        except Exception as e:
            print(f"An error occurred while executing the ban command: {e}")

            
    @app_commands.command(name="kick", description="Kick someone")
    @discord.app_commands.describe(member="The member you want to kick")
    @discord.app_commands.describe(reason="Why do you want to kick this member?")
    async def kick(self, interaction: discord.Interaction, member: discord.Member, *, reason: str = None):
        try:
            # Check if the bot has permission to kick members
            if not interaction.guild.me.guild_permissions.kick_members:
                raise discord.Forbidden("I do not have the permission to kick members.")

            # Check if the user has permission to kick members
            if not interaction.user.guild_permissions.kick_members:
                raise discord.Forbidden("You do not have the permission to kick members.")

            # Set a default reason if none is provided
            if reason is None:
                reason = "No reason provided"

            # Send a direct message to the kicked member
            embed = discord.Embed(title=f"You have been kicked from **{interaction.guild.name}**!", color=0x00D9FF,)
            embed.add_field(name="Kicked by", value=interaction.user.mention)
            embed.add_field(name="Reason", value=reason)
            await member.send(embed=embed)

            # Kick the member and provide the reason
            await member.kick(reason=f"{reason} | Kicked by: {interaction.user}")

            # Send a success message to the user
            embed = discord.Embed(title="Member kicked", color=0x00D9FF)
            embed.add_field(name="Kicked User", value=member.mention)
            embed.add_field(name="Kicked by", value=interaction.user.mention)
            embed.add_field(name="Reason", value=reason)
            await interaction.response.send_message(embed=embed, ephemeral=True)
                
        except discord.Forbidden as e:
            embed = discord.Embed(title="Error", color=0xff0000)
            embed.add_field(name="Message", value=str(e), inline=True)
            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            embed = discord.Embed(title="Error", color=0xff0000)
            embed.add_field(name="Message", value=str(e), inline=True)
            await interaction.response.send_message(embed=embed, ephemeral=True)





    @app_commands.command(name="lock_or_unlock", description="Locks or unlocks a channel")
    @discord.app_commands.describe(channel="The channel you want to lock or unlock")
    @discord.app_commands.describe(action="'lock' or 'unlock'")
    @discord.app_commands.describe(visibility="Should the channel be visible or invisible?")
    async def lock_or_unlock(self, interaction: discord.Interaction, channel: discord.TextChannel = None, action: Literal["lock", "unlock"] = "lock",
                            visibility: Literal["visible", "invisible"] = "visible"
    ):
        # Check if the bot has permission to manage channels
        bot_member = interaction.guild.get_member(self.bot.user.id)
        if not bot_member.guild_permissions.manage_channels:
            await interaction.response.send_message("I do not have the permission to manage channels.", ephemeral=True)
            return

        # Check if the user has permission to manage channels
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("You do not have the permission to lock or unlock channels.", ephemeral=True)
            return

        # If no channel is specified, lock or unlock the current channel
        channel = channel or interaction.channel

        # Get the permissions for the default role for the channel
        default_role = interaction.guild.default_role
        current_overwrite = channel.overwrites_for(default_role)

        # Determine the new permission overwrite for the default role
        if action == "unlock" and current_overwrite.send_messages == False:
            overwrite = discord.PermissionOverwrite(send_messages=None)
        elif action == "lock" and current_overwrite.send_messages != False:
            overwrite = discord.PermissionOverwrite(send_messages=False)
        else:
            await interaction.response.send_message(f"The channel is already {'locked' if action=='lock' else 'unlocked'}.", ephemeral=True)
            return

        # Set the new permissions for the default role
        try:
            await channel.set_permissions(default_role, overwrite=overwrite)
        except discord.Forbidden:
            await interaction.response.send_message(
                f"I do not have the permission to manage permissions for <#{channel.id}>.",
                ephemeral=True
            )
            return

        # If the channel is being made invisible, temporarily turn off permission syncing
        if visibility == "invisible":
            try:
                await channel.edit(sync_permissions=False)
            except discord.Forbidden:
                await interaction.response.send_message(f"I do not have the permission to edit the channel <#{channel.id}>.", ephemeral=True)
                return

        lockembed = discord.Embed(
            title=f"{action} channel",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        lockembed.add_field(name=f"The following channel has been {action}:", value=f"<#{channel.id}>")
        await interaction.response.send_message(embed=lockembed)

        # If the channel was made invisible, turn permission syncing back on
        if visibility == "invisible":
            try:
                await channel.edit(sync_permissions=True)
            except discord.Forbidden:
                await interaction.response.send_message(f"I do not have the permission to edit the channel <#{channel.id}>.", ephemeral=True)
                return




    @app_commands.command(name="nuke", description="Nuke a channel")
    @discord.app_commands.describe(channel="The channel you want to nuke")
    async def nuke(self, interaction: discord.Interaction, channel: discord.TextChannel = None): 
        # Check if the bot has permission to manage channels
        bot_member = interaction.guild.get_member(self.bot.user.id)
        if not bot_member.guild_permissions.manage_channels:
            await interaction.response.send_message("I do not have the permission to manage channels.", ephemeral=True)
            return
        
        # Check if the user has permission to manage channels
        if not interaction.user.guild_permissions.manage_channels:
            embed = discord.Embed(title="Permission Error", description=f"{interaction.user.mention}, you don't have enough permissions to use this command.",
                                  color=discord.Color.red()
            )
            embed.set_footer(text=f"Requested by {interaction.user.name}", icon_url=interaction.user.avatar)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Check if the bot has permission to manage channels
        if not interaction.guild.me.guild_permissions.manage_channels:
            embed = discord.Embed(title="Permission Error", description=f"I don't have enough permissions to nuke this channel.", color=discord.Color.red())
            embed.set_footer(text=f"Requested by {interaction.user.name}", icon_url=interaction.user.avatar)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        channel = channel or interaction.channel
        try:
            await interaction.response.send_message("Channel will be nuked shortly.", ephemeral=True)

            # Clone the channel and move it to the original channel's position, then delete the original channel
            new = await channel.clone(reason="Has been Nuked!")
            await new.edit(position=channel.position)
            await channel.delete()

            # Send an embed in the new channel to indicate that the nuke was successful
            embed = discord.Embed(title="Nuke Successful", description=f"This channel has been nuked!", color=discord.Color.red())
            embed.set_image(url="https://media.discordapp.net/attachments/811143476522909718/819507596302090261/boom.gif")
            embed.set_footer(text=f"Requested by {interaction.user.name}", icon_url=interaction.user.avatar)
            await new.send(embed=embed)
        except discord.HTTPException:
            embed = discord.Embed(title="Error", description=f"An error occurred while nuking the channel. Please try again later.", color=discord.Color.red())
            embed.set_footer(text=f"Requested by {interaction.user.name}", icon_url=interaction.user.avatar)
            await interaction.response.send_message(embed=embed, ephemeral=True)




    @app_commands.command(name="fakemessage", description="Fake a message from another member")
    @discord.app_commands.describe(member="The member you want to impersonate in the message.")
    @discord.app_commands.describe(message="The text you want to say")
    async def fakemessage(self, interaction: discord.Interaction, member: discord.Member, message: str):
        # Check if the user has the manage webhooks permission
        if not interaction.user.guild_permissions.manage_webhooks:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return
        
        try:
            # Create a webhook with the member's display name
            webhook_name = member.display_name
            webhook = await interaction.channel.create_webhook(name=webhook_name)

            # Send the fake message using the webhook
            await webhook.send(content=message, username=member.display_name, avatar_url=member.avatar)
            await interaction.response.send_message(f"Successfully sent fake message for {member.mention}", ephemeral=True)

        except discord.errors.Forbidden:
            await interaction.response.send_message(f"I cannot create a webhook in this channel.", ephemeral=True)
        
        except discord.errors.HTTPException as e:
            await interaction.response.send_message(f"Failed to send fake message: {e}", ephemeral=True)

        finally:
            # Delete the webhook after the fake message is sent
            if webhook:
                await webhook.delete()



async def setup(bot):
    await bot.add_cog(Admin(bot))

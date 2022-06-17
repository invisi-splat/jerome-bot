import discord
from discord.ext import commands
from discord.utils import get
import sqlite3
import os

def setup(client):

    print("Loading user channels...")

    # Database init

    con = sqlite3.connect("./data/user_channels.db")
    cur = con.cursor()

    try:
        cur.execute("SELECT * FROM ownership")
        cur.execute("SELECT * FROM channel_links")
    except sqlite3.OperationalError:
        print("No tables found. Creating table")
        cur.execute("CREATE TABLE ownership (channel CHAR(255), owner CHAR(255))")
        cur.execute("CREATE TABLE channel_links (channel CHAR(255), chain CHAR(255))")
        con.commit()

    class UserChannels(commands.Cog):
        def __init__(self, client):
            self.client = client
            guild = None
            for i in client.guilds:
                if i.id == int(os.environ["jeromes"]):
                    guild = i
            if guild == None:
                guild = client.guilds[0] # delete this before pushing
            self.category = get(guild.categories, id=int(os.environ["user_channel_category"]))
        
        # Notification

        async def broadcast(self, type, ctx, channel):
            if type == "delete":
                for member in channel.members:
                    try:
                        if not member.bot: await member.send(embed=discord.Embed(title="A user channel you were part of has been deleted", description=f"This is a friendly message to let you know that {ctx.author.name}, has deleted {channel.name}. As a result, you won't be able to see any messages sent in that channel - nor will anyone, in fact! It's all lost to the void now."))
                    except discord.errors.HTTPException:
                        await client.get_channel(int(os.environ["default_channel"])).send(embed=discord.Embed(title="A user channel you were part of has been deleted", description=f"""<@{member.id}> This is a friendly message to let you know that {ctx.author.name}, has deleted {channel.name}. As a result, you won't be able to see any messages sent in that channel - nor will anyone, in fact! It's all lost to the void now.
This message was sent here because there was an error DMing you."""))
                    except AttributeError:
                        continue
            elif type == "archive-auto":
                for member in channel.members:
                    await member.send(embed=discord.Embed(title="A user channel you were part of has been archived", description=f"The user channel {channel.name} has not seen any activity for over a week, and so it has been automatically archived. Don't worry - you can download all of the messages by clicking on the following link (if you so wish): "))
            elif type == "archive-man":
                for member in channel.members:
                    await member.send(embed=discord.Embed(title="A user channel you were part of has been archived", description=f"Just a friendly message to inform you that one of the owners of {channel.name}, {ctx.author.name}, has archived that user channel. You can download all of the messages by clicking on the following link (if you so wish): "))
            return


        # Channel creation and deletion

        @commands.command(aliases=["cr"])
        async def create(self, ctx, *args):
            print("Recieved create command.")
            args = list(args)
            try:
                if args[1] == "as":
                    args.pop(1)
                if args[1] == "text":
                    new_channel = await self.category.create_text_channel(args[0], reason=f"User channel created by {ctx.author.name}")
                    await new_channel.set_permissions(ctx.guild.default_role, read_messages=False, send_messages=False)
                    await new_channel.set_permissions(ctx.author, read_messages=True, send_messages=True)
                elif args[1] == "voice":
                    new_channel = await self.category.create_voice_channel(args[0], reason=f"User channel created by {ctx.author.name}")
                    await new_channel.set_permissions(ctx.guild.default_role, view_channel=False, send_messages=False, connect=False)
                    await new_channel.set_permissions(ctx.author, view_channel=True, send_messages=True, connect=True)
                await ctx.send(embed=discord.Embed(title="User channel created!", description=f"Go check it out at <#{new_channel.id}>!"))
            except IndexError:
                new_channel = await self.category.create_text_channel(args[0], reason=f"User channel created by {ctx.author.name}")
                await new_channel.set_permissions(ctx.guild.default_role, read_messages=False, send_messages=False)
                await new_channel.set_permissions(ctx.author, read_messages=True, send_messages=True)
            cur.execute(f"INSERT INTO ownership VALUES ({new_channel.id}, {ctx.author.id})")
            con.commit()
            print(f"Created a new user channel: {args[0]} by {ctx.author.name}")
            return
        
        @commands.command()
        async def archive(self, ctx, *, arg):
            return
        
        @commands.command()
        async def delete(self, ctx, *args):
            print("Received delete command.")
            if not args:
                await ctx.send(embed=discord.Embed(title="Error", description="No channel specified. (Tag the channel you wish to delete.)").set_footer(text="DELETE_NO_ARG"))
                return
            try:
                owners = cur.execute(f"SELECT owner FROM ownership WHERE channel={int(args[0][2:-1])}")
            except sqlite3.OperationalError:
                await ctx.send(embed=discord.Embed(title="Error", description="There was an error with either the database or your query.").set_footer(text="DELETE_SQL_FAIL"))
                return
            if str(ctx.author.id) not in owners.fetchall()[0]:
                await ctx.send(embed=discord.Embed(title="Error", description="You are not the owner of this channel.").set_footer(text="DELETE_INSIG_PERMS"))
                return
            else:
                target = client.get_channel(int(args[0][2:-1]))
                await self.broadcast("delete", ctx, target)
                await target.delete(reason="User generated channel deleted") # strip tag
                cur.execute(f"DELETE FROM ownership WHERE channel={int(args[0][2:-1])}")
                cur.execute(f"DELETE FROM channel_links WHERE channel={int(args[0][2:-1])}")
                con.commit()
                return

        # Owner management

        @commands.command()
        async def transfer(self, ctx, *, arg):
            return

        @commands.command()
        async def promote(self, ctx, *, arg):
            return

        @commands.command()
        async def resign(self, ctx, *, arg):
            return
        
        # User management

        @commands.command(aliases=["a"])
        async def add(self, ctx, *, arg):
            return
        
        @commands.command(aliases=["r"])
        async def remove(self, ctx, *, arg):
            return


        # Property management

        @commands.command(aliases=["ch"])
        async def change(self, ctx, *, arg):
            return

        @commands.command(aliases=["sh"])
        async def show(self, ctx, *, arg):
            return
        
        # Linking

        @commands.command(aliases=["lk"])
        async def link(self, ctx, *, arg):
            return
        
        @commands.command(aliases=["sever", "split", "unlk"])
        async def unlink(self, ctx, *, arg):
            return

        # Dev

        @commands.command()
        @commands.is_owner()
        async def clear(self, ctx):
            cur.execute("DROP TABLE ownership")
            cur.execute("DROP TABLE channel_links")
            con.commit()
            await ctx.send("\N{OK HAND SIGN}")

    client.add_cog(UserChannels(client))

    print("Loaded user channels.")
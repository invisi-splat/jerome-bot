import discord
from discord.ext import commands
import sqlite3

def setup(client):
    class UserChannels(commands.Cog):
        def __init__(self, client):
            self.client = client
        
        # Channel creation and deletion

        @commands.command(aliases=["cr"])
        async def create(self, ctx, *, arg):
            return
        
        @commands.command()
        async def archive(self, ctx, *, arg):
            return
        
        @commands.command()
        async def delete(self, ctx, *, arg):
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

    client.add_cog(UserChannels(client))
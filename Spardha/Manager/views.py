from django.shortcuts import render
from django.http import HttpResponseNotFound, HttpResponse
from Authentication.models import UserAccount
from Teams.models import Game, Team, Player
import csv

# Create your views here.
def user_data():
    users = []

    for user in Player.objects.all().order_by("name"):
        users.append(
            {
                "id": user.id,
                "name": user.name,
                "player": ("Captain" if user.is_captain else "Player"),
                "institution_name": user.team.college_rep.institution_name,
                "game": user.team.game.name,
                "members": user.team.num_of_players,
            }
        )
    return users


def game_data():
    games = []
    for game in Game.objects.all():
        games.append(
            {
                "id": game.id,
                "name": game.name,
            }
        )
    return games


def show_home(request):
    context = {
        "usersdata": user_data(),
        "gamesdata": game_data(),
    }

    if request.user.is_authenticated and request.user.is_admin:
        return render(request, "base.html", context)
    return HttpResponseNotFound("<h1>You are not allowed to visit this page!!!</h1>")


def table_to_response(name, table):
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=" + name + ".csv"},
    )

    writer = csv.writer(response)
    for row in table:
        writer.writerow(row)
    return response


def user_export(request, id):
    if request.user.is_authenticated and request.user.is_admin:
        user = Player.objects.get(id=id)
        data = [["User Details"]]
        data = [
            ["Name", user.name],
            ["Role", ("Captain" if user.is_captain else "Player")],
            ["Institution Name", user.team.college_rep.institution_name],
            ["Game", user.team.game.name],
            ["Total Members", user.team.num_of_players],
        ]
        group = Player.objects.filter(name=user.name)
        data.append([])
        data.append(["All Games", "Players"])
        for object in group:
            data.append([object.team.game.name, object.team.num_of_players])

        return table_to_response(user.name.replace(" ", ""), data)
    return HttpResponseNotFound("<h1>You are not allowed to visit this page!!!</h1>")


def game_export(request, id):
    if request.user.is_authenticated and request.user.is_admin:
        game = Game.objects.get(id=id)
        data = [["College Name", "Members", "Captain"]]
        for i in range(1, game.max_players + 1):
            data[0].append("Player " + str(i))
        for team in Team.objects.filter(game=game):
            arr = [team.college_rep.institution_name, team.num_of_players]
            try:
                arr.append(Player.objects.get(team=team, is_captain=True).name)
            except:
                arr.append("No Captain")
            for player in Player.objects.filter(team=team, is_captain=False):
                arr.append(player.name)
            data.append(arr)
        return table_to_response(game.name.replace(" ", ""), data)
    return HttpResponseNotFound("<h1>You are not allowed to visit this page!!!</h1>")


def all_export(request):
    if request.user.is_authenticated and request.user.is_admin:
        data = [["Name", "Role", "Institution Name", "Game", "Members"]]
        for player in Player.objects.all().order_by("name"):
            data.append(
                [
                    player.name,
                    ("Captain" if player.is_captain else "Player"),
                    player.team.college_rep.institution_name,
                    player.team.game.name,
                    player.team.num_of_players,
                ]
            )
        return table_to_response("AllUsers", data)
    return HttpResponseNotFound("<h1>You are not allowed to visit this page!!!</h1>")

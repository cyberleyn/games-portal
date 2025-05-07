from flask import Flask, render_template, request, url_for, redirect, make_response

from repository.repository import Repository

app = Flask(__name__)


@app.route("/", methods=['post', 'get'])
def index():
    if request.method == "GET":
        if not request.cookies.get("user"):
            return redirect(url_for("login"))
        else:
            userid = request.cookies.get("user")
            return redirect(url_for("profile", id=userid))


@app.route("/login", methods=['post', 'get'])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form.get("uname")
        password = request.form.get("psw")
        auth = Repository.auth(username, password)
        if auth["success"]:
            userid = auth["user"].id
            response = make_response(redirect(url_for("profile", id=auth["user"].id)))
            response.set_cookie('user', str(userid))
            return response
        else:
            return render_template("login.html", error=True)


@app.route("/register", methods=['post', 'get'])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        user = Repository.register()
        response = make_response(redirect(url_for("profile", id=user.id)))
        response.set_cookie("user", str(user.id))
        return response


@app.route("/profile/<string:id>", methods=['GET', 'POST'])
def profile(id):
    user = Repository.get_user_by_id(id)
    invite = Repository.get_pending_invites(user)
    can_edit = Repository.can_edit(user.id)
    error = request.args.get('error')
    print("Has Invite", error)
    pending_invite = Repository.check_friendship(user.id)
    friends = Repository.get_friends(user)
    return render_template("profile.html", user=user, can_edit=can_edit, invites=invite, pending_invite=pending_invite,
                           friends=friends, error=error)


@app.route("/profile/<string:id>/edit", methods=['GET', 'POST'])
def profile_edit(id):
    user = Repository.get_user_by_id(id)
    can_edit = Repository.can_edit(user.id)
    if not can_edit:
        return redirect(url_for("index"))
    if request.method == "GET":
        return render_template("edit.html", user=user)
    if request.method == "POST":
        if 'user-steam' in request.form:
            Repository.connect_steam(id, request.form.get("user-steam"))
        else:
            Repository.save_user_changes(user)
        return redirect(url_for("profile", id=user.id))


@app.route("/profile/logout", methods=['GET', 'POST'])
def logout():
    response = make_response(redirect(url_for("index")))
    response.set_cookie('user', "", max_age=0)
    return response


@app.route("/profile/<string:id>/invite", methods=['GET', 'POST'])
def add_friend(id):
    if not request.cookies.get("user"):
        return redirect(url_for("login"))
    else:
        userid = request.cookies.get("user")
        friendid = Repository.get_user_by_id(id)
        invite = Repository.add_friend(userid, friendid)
        error = invite is None
        return redirect(url_for("profile", id=id, error=error))


@app.route("/accept_invite/<string:id>", methods=['GET', 'POST'])
def accept_invite(id):
    Repository.accept_invite(id)
    user = request.cookies.get("user")
    return redirect(url_for("profile", id=user))


@app.route("/decline_invite/<string:id>", methods=['GET', 'POST'])
def decline_invite(id):
    Repository.decline_invite(id)
    user = request.cookies.get("user")
    return redirect(url_for("profile", id=user))


@app.route("/profile/<string:id>/inventory", methods=['GET', 'POST'])
def inventory(id):
    user = Repository.get_user_by_id(id)
    can_edit = Repository.can_edit(user.id)
    inventory = Repository.get_user_inventory(id)
    return render_template("inventory.html", user=user, can_edit=can_edit, inventory=inventory)


@app.route("/profile/<string:id>/offers", methods=['GET', 'POST'])
def offers(id):
    user = Repository.get_user_by_id(id)
    can_edit = Repository.can_edit(user.id)
    offers = Repository.get_offers(user)
    curent_user_id = request.cookies.get("user")
    curent_user = Repository.get_user_by_id(curent_user_id)
    return render_template("offers.html", user=user, can_edit=can_edit, offers=offers, curent_user=curent_user)


@app.route("/profile/<string:id>/create_offer", methods=['GET', 'POST'])
def create_offer(id):
    sender_id = request.cookies.get("user")
    sender = Repository.get_user_by_id(sender_id)
    receiver = Repository.get_user_by_id(id)
    if sender == receiver:
        return render_template("errorpage.html", user=sender)
    if request.method == "POST":
        sender_items = request.form.getlist('sender-items')
        print(sender_items)
        receiver_items = request.form.getlist('receiver-items')
        print(receiver_items)
        items = sender_items + receiver_items
        Repository.create_offer(sender, receiver, items)
        return redirect(url_for("profile", id=sender_id))
    sender_inventory = Repository.get_user_inventory(sender_id)
    receiver_inventory = Repository.get_user_inventory(receiver.id)
    return render_template("createoffer.html", sender=sender, receiver=receiver, sender_inventory=sender_inventory,
                           receiver_inventory=receiver_inventory)


@app.route("/decline_offer/<string:id>", methods=['GET', 'POST'])
def decline_offer(id):
    offer = Repository.get_offer_by_id(id)
    Repository.delete_offer(offer)
    user = request.cookies.get("user")
    return redirect(url_for("profile", id=user))


@app.route("/accept_offer/<string:id>", methods=['GET', 'POST'])
def accept_offer(id):
    offer = Repository.get_offer_by_id(id)
    Repository.accept_offer(offer)
    user = request.cookies.get("user")
    return redirect(url_for("profile", id=user))


@app.route("/myprofile")
def get_my_profile():
    user = request.cookies.get("user")
    return redirect(url_for("profile", id=user))


@app.route("/myinventory")
def get_my_inventory():
    user = request.cookies.get("user")
    return redirect(url_for("inventory", id=user))


@app.route("/users")
def users():
    users = Repository.get_all_users()
    return render_template("users.html", users=users)


@app.route("/myfriends")
def friends():
    if not request.cookies.get("user"):
        return redirect(url_for("login"))
    else:
        userid = request.cookies.get("user")
        user = Repository.get_user_by_id(userid)
        invites = Repository.get_pending_invites(user)
        friends = Repository.get_friends(user)
        return render_template("friends.html", friends=friends, invites=invites)


@app.route("/mygames")
def my_games():
    if not request.cookies.get("user"):
        return redirect(url_for("login"))
    else:
        userid = request.cookies.get("user")
        return redirect(url_for("games", id=userid))


@app.route("/profile/<string:id>/games", methods=['GET', 'POST'])
def games(id):
    user = Repository.get_user_by_id(id)
    can_edit = Repository.can_edit(user.id)
    games = Repository.get_user_games(id)
    return render_template("games.html", games=games)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)

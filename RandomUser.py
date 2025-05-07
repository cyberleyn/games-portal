from coolname import generate

def create_creds():
    words = generate()
    username = ""
    nickname = ""
    approved = 0
    for word in words:
        if len(word) > 2:
            approved += 1
            nickname += word.capitalize()
            if approved == 1:
                username += word
        if approved == 2:
            break
    return {"username": username, "nickname": nickname}

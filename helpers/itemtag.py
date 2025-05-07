class ItemTag:

    def __init__(self):
        self.category = None
        self.internal_name = None
        self.localized_category_name = None
        self.localized_tag_name = None
        self.color = ""


    def from_json(self, json):
        self.category = json["category"]
        self.internal_name = json["internal_name"]
        self.localized_category_name = json["localized_category_name"]
        self.localized_tag_name = json["localized_tag_name"]
        try:
            self.color = "#" + json["color"]
        except KeyError:
            pass


        return self

    def to_dict(self):
        return {'category': self.category, "internal_name": self.internal_name, "color": self.color}
from scene import Scene


class JackNinjasInventory(Scene):
    EQUIPPABLE_WEAPONS = {"glaive", "boomerang"}
    ITEM_LABELS = {
        "double_jump": "Double Jump",
        "glaive": "Glaive",
        "boomerang": "Boomerang",
    }

    def __init__(self, game):
        super().__init__(game)
        self.selected = 0
        self.status_text = ""
        self.status_timeout = 0.0
        self.standard_font_size = 20

    def inventory_items(self):
        return list(getattr(self.game, "inventory", []))

    def item_label(self, item_name: str):
        return self.ITEM_LABELS.get(item_name, item_name.replace("_", " ").title())

    def active_weapon(self):
        return getattr(self.game, "jack_ninjas_active_weapon", None)

    def clamp_selection(self):
        items = self.inventory_items()
        if not items:
            self.selected = 0
        else:
            self.selected = max(0, min(self.selected, len(items) - 1))

    def update(self):
        if self.game.input["cancel"].just_pressed or self.game.input["inventory"].just_pressed:
            self.game.scene_pop = True
            return

        items = self.inventory_items()
        self.clamp_selection()

        if not items:
            return

        if self.game.input["down"].just_pressed:
            self.selected = (self.selected + 1) % len(items)
            self.play_sound("click")

        if self.game.input["up"].just_pressed:
            self.selected = (self.selected - 1) % len(items)
            self.play_sound("click")

        if self.game.input["confirm"].just_pressed:
            selected_item = items[self.selected]
            if selected_item in self.EQUIPPABLE_WEAPONS:
                self.game.jack_ninjas_active_weapon = selected_item
                self.status_text = "Equipped: " + self.item_label(selected_item)
                self.play_sound("jsxfr-select")
            else:
                self.status_text = self.item_label(selected_item) + " is passive."
                self.play_sound("click")
            self.status_timeout = self.elapsed() + 1.5

    def draw(self):
        self.draw_rect_alpha(
            self.screen,
            (0, 0, 0, 220),
            (0, 0, self.screen.get_width(), self.screen.get_height()),
        )

        title = self.standard_text("Inventory", font_size=32)
        title_rect = title.get_rect(center=(self.screen.get_width() // 2, 28))
        self.screen.blit(title, title_rect)

        items = self.inventory_items()
        active_weapon = self.active_weapon()

        if not items:
            empty_text = self.standard_text("No items collected yet.", font_size=18)
            empty_rect = empty_text.get_rect(center=(self.screen.get_width() // 2, 90))
            self.screen.blit(empty_text, empty_rect)
        else:
            start_x = 30
            start_y = 70
            y_spacing = 24
            for i, item_name in enumerate(items):
                line = self.item_label(item_name)
                if item_name in self.EQUIPPABLE_WEAPONS and item_name == active_weapon:
                    line += " [equipped]"
                elif item_name not in self.EQUIPPABLE_WEAPONS:
                    line += " (passive)"

                prefix = "> " if i == self.selected else "  "
                line_surface = self.standard_text(prefix + line, font_size=18)
                line_surface.set_alpha(255 if i == self.selected else 180)
                self.screen.blit(line_surface, (start_x, start_y + i * y_spacing))

        hint = self.standard_text(
            "Up/Down: Select  Enter/Space: Equip  I/Esc: Close",
            font_size=14,
        )
        hint_rect = hint.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() - 18))
        self.screen.blit(hint, hint_rect)

        if self.status_text and self.elapsed() <= self.status_timeout:
            status = self.standard_text(self.status_text, font_size=16)
            status_rect = status.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() - 44))
            self.screen.blit(status, status_rect)

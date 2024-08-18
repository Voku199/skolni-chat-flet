class ChatMessage(ft.Row, str):
    def __init__(self, message: Message):
        super().__init__()
        self.vertical_alignment = "start"
        user_info = message.user_name
        # image_bytes = base64.b64decode(message.user_profile_picture)
        # chat_message = ChatMessage(message, user_profile_picture=image_bytes)
        # user_profile_picture: bytes | None = None

        self.message = message
        self.controls = [
            ft.Row(
                controls=[
                    message.user_profile_picture,  # Zobrazit profilovou fotku
                    ft.Column(
                        controls=[
                            ft.Text(message.user_name, weight=ft.FontWeight.BOLD),
                            ft.Text(message.text),
                        ]
                    ),
                ]
            )
        ]

        m = []

        if message.user_name:
            m = [
                ft.Text(message.user_name, weight="bold", color=ft.colors.WHITE),
                ft.Text(message.text, selectable=True, width=message.page.width - 100),
                # self.parse_message_content(message.text),
            ]

        if message.user_role != None:
            user_info += f" [{message.user_role}]"
            m = [
                ft.Text(user_info, weight="bold", color=ft.colors.YELLOW),
                ft.Text(message.text, selectable=True, width=message.page.width - 100),
                # self.parse_message_content(message.text),
            ]

        avatar = ft.CircleAvatar(
            content=ft.Text(
                self.get_initials(
                    message.user_name,
                )
            ),
            color=ft.colors.WHITE,
            bgcolor=self.get_avatar_color(
                message.user_name,
            ),
        )

        if message.user_profile_picture:
            avatar = ft.CircleAvatar(
                content=ft.Image(
                    src_base64=message.user_profile_picture.decode("ascii"),
                    width=50,
                    height=50,
                ),
                color=ft.colors.TRANSPARENT,
            )

        # text1 = "má profilovku",

        # if message.user_profile_picture:
        #     user_info += f"{text1}"
        #     m = [
        #         ft.Text(user_info, weight="bold", color=ft.colors.RED),
        #         ft.Text(message.text, selectable=True, width=message.page.width - 100),
        #         #self.parse_message_content(message.text),
        #     ]

        #     avatar = ft.CircleAvatar(
        #         content=ft.Image(src_base64=message.user_profile_picture, width=50, height=50),
        #         color=ft.colors.TRANSPARENT
        #     )

        self.controls = [
            avatar,
            ft.Column(
                m,
                tight=True,
                spacing=5,
            ),
        ]

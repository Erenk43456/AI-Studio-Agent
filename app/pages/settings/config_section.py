from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QDoubleSpinBox,
    QSpinBox,
    QPushButton
)



class ConfigSection(QWidget):


    def __init__(self, config):

        super().__init__()


        self.config = config


        layout = QVBoxLayout()





        temp_label = QLabel(
            "Temperature"
        )


        self.temperature_box = QDoubleSpinBox()


        self.temperature_box.setRange(
            0.0,
            1.0
        )


        self.temperature_box.setSingleStep(
            0.1
        )





        token_label = QLabel(
            "Max Tokens"
        )


        self.token_box = QSpinBox()


        self.token_box.setRange(
            50,
            2000
        )





        self.save_button = QPushButton(
            "Save Settings"
        )


        self.save_button.clicked.connect(
            self.save
        )





        self.status = QLabel(
            ""
        )





        layout.addWidget(
            temp_label
        )


        layout.addWidget(
            self.temperature_box
        )


        layout.addWidget(
            token_label
        )


        layout.addWidget(
            self.token_box
        )


        layout.addWidget(
            self.save_button
        )


        layout.addWidget(
            self.status
        )



        self.setLayout(
            layout
        )


        self.load()







    def load(self):


        self.temperature_box.setValue(

            self.config.get(
                "temperature",
                0.3
            )

        )


        self.token_box.setValue(

            self.config.get(
                "num_predict",
                150
            )

        )







    def save(self):


        self.config.update(

            {

                "temperature":
                self.temperature_box.value(),


                "num_predict":
                self.token_box.value()

            }

        )


        self.config.save()



        self.status.setText(
            "✅ Settings saved"
        )
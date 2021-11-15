import numpy as np
from tensorflow.keras.datasets import mnist
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import MaxPooling2D
from tensorflow.keras.layers import Activation
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Dropout
from tensorflow.keras.utils import to_categorical


class TrainDigitReader:
    __x_train = None
    __x_test = None
    __y_train = None
    __y_test = None
    __numClasses = None
    __inputShape = None
    digitReader = None

    def __init__(self):
        # MNIST dataset training and test sets
        (self.__x_train, self.__y_train), (self.__x_test, self.__y_test) = mnist.load_data()
        self.__numClasses = 10
        self.__inputShape = (28, 28, 1)

    def preprocessModel(self):
        # Scale images to the [0, 1] range
        self.__x_train = self.__x_train.astype("float32") / 255
        self.__x_test = self.__x_test.astype("float32") / 255
        # Make sure images have shape (28, 28, 1)
        self.__x_train = np.expand_dims(self.__x_train, -1)
        self.__x_test = np.expand_dims(self.__x_test, -1)

        # convert class vectors to binary class matrices
        self.__y_train = to_categorical(self.__y_train, self.__numClasses)
        self.__y_test = to_categorical(self.__y_test, self.__numClasses)

    def buildModel(self):
        self.digitReader = Sequential(
            [
                Conv2D(32, (5, 5), padding="same", input_shape=self.__inputShape),
                Activation("relu"),
                MaxPooling2D(pool_size=(2, 2)),

                Conv2D(32, (3, 3), padding="same"),
                Activation("relu"),
                MaxPooling2D(pool_size=(2, 2)),

                Flatten(),
                Dense(64),
                Activation("relu"),
                Dropout(0.5),

                Dense(64),
                Activation("relu"),
                Dropout(0.5),

                Dense(self.__numClasses),
                Activation("softmax")
            ]
        )
        self.digitReader.summary()

    def compileModel(self):
        self.digitReader.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"])
        self.digitReader.fit(self.__x_train, self.__y_train, batch_size=128, epochs=15, validation_split=0.1)
        score = self.digitReader.evaluate(self.__x_test, self.__y_test, verbose=0)
        print("Test loss:", score[0])
        print("Test accuracy:", score[1])
        self.digitReader.save("model/digitReader.h5")


objTrainer = TrainDigitReader()
objTrainer.preprocessModel()
objTrainer.buildModel()
objTrainer.compileModel()

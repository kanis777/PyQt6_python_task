import sys
import requests
from PyQt6.QtWidgets import QApplication, QPushButton, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsProxyWidget, QSlider, QVBoxLayout, QWidget,QGraphicsSimpleTextItem
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt
from bs4 import BeautifulSoup
import random
from PIL import Image

#to create a canvas with our requirement
class CanvasView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        #to set the dimension of the scene
        self.scene.setSceneRect(0, 0, 400, 300)
        self.setScene(self.scene)
        #creating 2 buttons with our requirements
        button1 = QPushButton("Button 1")
        proxy_button1 = QGraphicsProxyWidget()
        proxy_button1.setWidget(button1)
        """BUTTON 1 REQUIREMENTS:When clicked, a random geometric image from url should be downloaded and rendered at any random location on the canvas. 
        It should be selectable and movable. An image from that repository should keep on appearing whenever this button is clicked, 
        without removing/overwriting the previous images (compulsory)."""
        proxy_button1.setPos(50, 50)
        button2 = QPushButton("Button 2")
        proxy_button2 = QGraphicsProxyWidget()
        proxy_button2.setWidget(button2)
        proxy_button2.setPos(150, 50)
        self.scene.addItem(proxy_button1)
        self.scene.addItem(proxy_button2)
        button1.clicked.connect(self.download_random_image)#when button1 is clicked it will download a random image from the url
        self.image_items = []
        self.scene.sceneRectChanged.connect(self.adjust_image_positions)
        self.size_label = QGraphicsSimpleTextItem()
        self.color_label = QGraphicsSimpleTextItem()
        self.location_label = QGraphicsSimpleTextItem()
        self.slider = QSlider(Qt.Orientation.Vertical)  #Here we have used a slider to make sure we can change the size of the image we have .
        #Note:This slider changes the size for all the images present in our canvas and not particular image
        self.slider.setMinimum(1)
        self.slider.setMaximum(10)
        self.slider.setValue(5)
        self.slider.setTickInterval(1)
        self.slider.setTickPosition(QSlider.TickPosition.TicksRight)
        self.slider.valueChanged.connect(self.resize_image)
        layout = QVBoxLayout()
        layout.addWidget(self.slider)
        widget = QWidget()
        widget.setLayout(layout)
        proxy_slider = QGraphicsProxyWidget()
        proxy_slider.setWidget(widget)
        proxy_slider.setPos(250, 50)#for comfortable access the slider has been set right next to button 2
        self.scene.addItem(proxy_slider)

    def download_random_image(self):
        search_url = "https://www.google.com/search?q=images+with+one+colored+geometric+single+figures&tbm=isch&ved=2ahUKEwjurtOm8oj_AhVSi9gFHRiuBKoQ2-cCegQIABAA&oq=images+with+one+colored+geometric+single+figures&gs_lcp=CgNpbWcQA1CbGViKHGC3HmgAcAB4AIABYogB9QKSAQE0mAEAoAEBqgELZ3dzLXdpei1pbWfAAQE&sclient=img&ei=fltrZO73FdKW4t4PmNyS0Ao&bih=632&biw=1422&rlz=1C1RXQR_enIN999IN999"
        response = requests.get(search_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            image_elements = soup.select("img")
            if image_elements:
                random_image_element = random.choice(image_elements)
                image_url = random_image_element["src"]
                response = requests.get(image_url)
                if response.status_code == 200:
                    with open("random_image.jpg", "wb") as file:
                        file.write(response.content)
                    print("Image downloaded successfully!")
                    self.display_image()
                else:
                    print("Failed to download image.")
            else:
                print("No image found on the search page.")
        else:
            print("Failed to fetch search page.")

    def display_image(self):
        pixmap = QPixmap("random_image.jpg")
        if not pixmap.isNull():
            pixmap_item = QGraphicsPixmapItem(pixmap)
            pixmap_item.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, True)#to make sure that we can drag and drop our images i.e., to make it movable
            colliding_items = pixmap_item.collidingItems()#attempt to make sure there is no overlap of the images (unfortunately not very successful)
            while colliding_items:
                pixmap_item.setPos(pixmap_item.x() + 10, pixmap_item.y() + 10)
                colliding_items = pixmap_item.collidingItems()
            self.scene.addItem(pixmap_item)
            self.image_items.append(pixmap_item)
            image_path = "random_image.jpg"
            image = Image.open(image_path)
            #to find the size,location and color of the image
            image_size = image.size
            image_color = image.getcolors(256)
            image_location = pixmap_item.pos()
            self.size_label.setText("Size: " + str(image_size))
            self.size_label.setPos(image_location.x(), image_location.y() + pixmap.height() + 10)
            self.size_label.setFont(QFont("Arial", 10))
            self.scene.addItem(self.size_label)#to display the details in the canvas
            self.color_label.setText("Colors: " + str(image_color))
            self.color_label.setPos(image_location.x(), image_location.y() + pixmap.height() + 30)
            self.color_label.setFont(QFont("Arial", 10))
            self.scene.addItem(self.color_label)
            self.location_label.setText("Location: " + str(image_location))
            self.location_label.setPos(image_location.x(), image_location.y() + pixmap.height() + 50)
            self.location_label.setFont(QFont("Arial", 10))
            self.scene.addItem(self.location_label)
        else:
            print("Failed to load image.")

    def adjust_image_positions(self, rect):
        for i, item in enumerate(self.image_items):#to adjust so they don't overlap(sadly this was not successful either )
            image_width = item.pixmap().width()
            image_height = item.pixmap().height()
            offset_x = (i % 3) * (image_width + 10)
            offset_y = (i // 3) * (image_height + 10)
            item.setPos(offset_x, offset_y)
            self.size_label.setPos(offset_x, offset_y + image_height + 10)
            self.color_label.setPos(offset_x, offset_y + image_height + 30)
            self.location_label.setPos(offset_x, offset_y + image_height + 50)

    def resize_image(self, value):#to resize the image with the slider 
        scale_factor = value / 5.0  
        for item in self.image_items:
            pixmap = item.pixmap()
            new_width = int(pixmap.width() * scale_factor)
            new_height = int(pixmap.height() * scale_factor)
            new_pixmap = pixmap.scaled(new_width, new_height)
            item.setPixmap(new_pixmap)

app = QApplication(sys.argv)
window = QMainWindow()
canvas = CanvasView()
window.setCentralWidget(canvas)
window.show()
app.exec()

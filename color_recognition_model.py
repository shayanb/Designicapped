# USAGE
# python color_kmeans.py --image images/jp.png --clusters 3

# import the necessary packages
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import utils
import cv2


# load the image and convert it from BGR to RGB so that

def get_top_n_colors(image_path, n_cluster):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # show original image
    # show_image(image)
    image = image.reshape((image.shape[0] * image.shape[1], 3))

    # cluster the pixel intensities
    clt = KMeans(n_clusters = n_cluster)
    clt.fit(image)

    # build a histogram of clusters and then create a figure
    # representing the number of pixels labeled to each color
    hist = utils.centroid_histogram(clt)

    # RGB
    #bar = utils.plot_colors(hist, clt.cluster_centers_)
    # show our color bar
    # show_image(bar)

    # show both images
    # plt.show()

    Cluster_center = [[int(elem) for elem in myList] for myList in clt.cluster_centers_]
    Proportion = [round(elem * 100, 2) for elem in hist]

    return  zip(Cluster_center, Proportion)


def show_image(object):
    plt.figure()
    plt.axis("off")
    plt.imshow(object)



# reshape the image to be a list of pixels


print(get_top_n_colors("Sample.jpg", 3))
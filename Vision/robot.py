#!/usr/bin/env python2

import os
import time

from google.protobuf import text_format
import numpy as np
import PIL.Image
import scipy.misc
import operator

os.environ['GLOG_minloglevel'] = '2' # Supress most Caffe output
import caffe
from caffe.proto import caffe_pb2

# Constants
deploy_file = '/home/ubuntu/deploy.prototxt' # path to .prototxt file
caffemodel = '/home/ubuntu/testnetwork.caffemodel' # path to .caffemodel file
test_image = '/home/ubuntu/test4.jpg'
test2 = '/home/ubuntu/test5.jpg'
batch_size = 8
camera_resolution = (720, 1024)
minimum = 70.0 # Minimum confidence value to fire at a target

# (x, y, width height)
#boxes = {'0' : (60, 112, 325, 367), '1' : (213, 240, 469, 496), '2' : (316, 368, 572, 624), '3' : (746, 50, 1002, 306), '4' : (384, 50, 640, 306), '5' : (400, 384, 656, 640), '6' : (750, 454, 1006, 710), '7' : (470, 245, 726, 501)}
boxes = {'0' : (60, 112, 256, 256), '1' : (213, 240, 256, 256), '2' : (316, 368, 256, 256), '3' : (746, 50, 256, 256), '4' : (384, 50, 256, 256), '5' : (400, 384, 256, 256), '6' : (750, 424, 256, 256), '7' : (470, 245, 256, 256)}

class Robot(object):

    def __init__(self):
        caffe.set_mode_gpu()
        self.net = caffe.Net(deploy_file, caffemodel, caffe.TEST)
        self.transformer = self.get_transformer()
        self._, self.channels, self.height, self.width = self.transformer.inputs['data']
        if self.channels == 3:
            self.mode = 'RGB'
        elif self.channels == 1:
            self.mode = 'L'
        else:
            raise ValueError('Invalid number for channels: %s' % self.channels)
        self.target = None
        self.testClassify()

    def get_transformer(self):
        network = caffe_pb2.NetParameter()

        with open(deploy_file) as infile:
            text_format.Merge(infile.read(), network)

        if network.input_shape:
            dims = network.input_shape[0].dim
        else:
            dims = network.input_dim[:4]

        t = caffe.io.Transformer(inputs={'data':dims})
        t.set_transpose('data', (2, 0, 1))

        if dims[1] == 3:
            t.set_channel_swap('data', (2, 1, 0))

        return t

    def load_image(self, path, height, width, mode='RGB'):
        image = PIL.Image.open(path)
        image = image.convert(mode)
        image = np.array(image)
        image = scipy.misc.imresize(image, (height, width), 'bilinear')
        return image

    def listImage(self, image):
        # image = PIL.Image.open(path)
        # image = np.array(image)
        myimage = np.copy(image)
        myimage = scipy.misc.imresize(myimage, camera_resolution)
        windowList  = []
        windowList.append(myimage[112:367, 60:325]) # image[y1:y2, x1:x2]
        windowList.append(myimage[240:496, 213:469])
        windowList.append(myimage[368:624, 316:572])
        windowList.append(myimage[50:306, 746:1002])
        windowList.append(myimage[50:306, 384:640])
        windowList.append(myimage[384:640, 400:656])
        windowList.append(myimage[454:710, 750:1006])
        windowList.append(myimage[245:501, 470:726])

        return windowList


    def forward_pass(self, images, batch):
        if batch is None:
            batch = 1

        caffe_images = []
        for image in images:
            if image.ndim == 2:
                caffe_images.append(image[:, :, np.newaxis])
            else:
                caffe_images.append(image)

        dims = self.transformer.inputs['data'][1:]

        scores = None
        for chunk in [caffe_images[x:x + batch_size] for x in xrange(0, len(caffe_images), batch_size)]:
            new_shape = (len(chunk),) + tuple(dims)
            if self.net.blobs['data'].data.shape != new_shape:
                self.net.blobs['data'].reshape(*new_shape)
            for index, image in enumerate(chunk):
                image_data = self.transformer.preprocess('data', image)
                self.net.blobs['data'].data[index] = image_data
            start = time.time()
            output = self.net.forward()[self.net.outputs[-1]]
            end = time.time()
            if scores is None:
                scores = np.copy(output)
            else:
                scores = np.vstack((scores, output))
            print 'Processed %s/%s images in %f seconds ..' % (len(scores), len(caffe_images), (end - start))

        return scores

    def testClassify(self):
        images = [self.load_image(test_image, self.height, self.width, self.mode)]
        scores = self.forward_pass(images, 1)
        if scores is None:
            print 'Error classifying test image'
        else:
            print 'Robot object is ready for classifying.'


    def classify(self, image_files):
        # images = [load_image(image_file, self.height, self.width, self.mode) for image_file in image_files]
        images = self.listImage(image_files)
        scores = self.forward_pass(images, batch_size)

        indices = (-scores).argsort()[:, :5]
        classifications = []
        for image_index, index_list in enumerate(indices):
            result = []
            for i in index_list:
                label = 'Class #%s' % i
                result.append((label, round(100.0 * scores[image_index, i], 4)))
            classifications.append(result)

        sums = []
        for index, classification in enumerate(classifications):
            # print '{:-^80}'.format(' Prediction for %s ' % index)
            indexSum = 0.0
            for label, confidence in classification:
               # print '{:9.4%} - "{}"'.format(confidence/100.0, label)
               if label != "Class #4":
                   num = '{:9.4}'.format(confidence/1.0)
                   indexSum += float(num)
            sums.append((index, indexSum))

        sums.sort(key=operator.itemgetter(1))
        index, value = sums[7]
        if value > minimum:
            self.target = np.array([boxes[str(index)]])
            return self.target
        else:
            self.target = np.array([])
            return self.target




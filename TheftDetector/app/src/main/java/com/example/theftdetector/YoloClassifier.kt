package com.example.theftdetector


import android.content.Context
import android.graphics.Bitmap
import org.tensorflow.lite.Interpreter
import java.io.FileInputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.nio.channels.FileChannel

class YoloClassifier(context: Context) {
    private val interpreter: Interpreter
    private val inputSize = 640

    init {
        val model = loadModel(context, "yolov8n_float32.tflite")
        interpreter = Interpreter(model)
    }

    private fun loadModel(context: Context, filename: String): ByteBuffer {
        val fileDescriptor = context.assets.openFd(filename)
        val inputStream = FileInputStream(fileDescriptor.fileDescriptor)
        val fileChannel = inputStream.channel
        return fileChannel.map(FileChannel.MapMode.READ_ONLY, fileDescriptor.startOffset, fileDescriptor.declaredLength)
    }

    fun detect(bitmap: Bitmap): List<String> {
        val resizedBitmap = Bitmap.createScaledBitmap(bitmap, inputSize, inputSize, true)
        val inputBuffer = ByteBuffer.allocateDirect(1 * inputSize * inputSize * 3 * 4)
        inputBuffer.order(ByteOrder.nativeOrder())

        val pixels = IntArray(inputSize * inputSize)
        resizedBitmap.getPixels(pixels, 0, inputSize, 0, 0, inputSize, inputSize)
        for (pixel in pixels) {
            inputBuffer.putFloat(((pixel shr 16 and 0xFF) / 255f))
            inputBuffer.putFloat(((pixel shr 8 and 0xFF) / 255f))
            inputBuffer.putFloat(((pixel and 0xFF) / 255f))
        }

        // Allocate as per model output [1, 84, 8400]
        val outputBuffer = Array(1) { Array(84) { FloatArray(8400) } }

        interpreter.run(inputBuffer, outputBuffer)

        // Transpose it to [8400][84] for parsing
        val transposedOutput = Array(8400) { FloatArray(84) }
        for (i in 0 until 84) {
            for (j in 0 until 8400) {
                transposedOutput[j][i] = outputBuffer[0][i][j]
            }
        }

        return parse(transposedOutput)
    }


    private fun parse(output: Array<FloatArray>): List<String> {
        val labels = listOf(
            // Original COCO labels
            "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat",
            "traffic light", "fire hydrant", "stop sign", "parking meter", "bench",
            "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe",
            "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball",
            "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket",
            "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl",
            "banana", "apple", "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake",
            "chair", "couch", "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse", "remote",
            "keyboard", "cell phone", "microwave", "oven", "toaster", "sink", "refrigerator",
            "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush",

            // Additional objects (extended)
            "fan", "helmet", "wallet", "power bank", "speaker", "tablet", "monitor", "router", "lamp", "router",
            "shoes", "slippers", "t-shirt", "pants", "jeans", "jacket", "hat", "cap", "sunglasses", "gloves",
            "watch", "ring", "necklace", "bracelet", "earphones", "headphones", "tripod", "camera", "dslr",
            "mug", "plate", "pan", "kettle", "blender", "mixer", "juicer", "rice cooker", "water bottle",
            "lighter", "matchbox", "gas stove", "gas cylinder", "iron box", "sewing machine",
            "notebook", "diary", "pen", "pencil", "highlighter", "stapler", "eraser", "scale", "calculator",
            "toolbox", "hammer", "wrench", "screwdriver", "pliers", "drill machine", "tape", "glue",
            "broom", "mop", "bucket", "dustbin", "spray bottle", "washing machine", "laundry basket",
            "toy car", "soft toy", "lego", "puzzle", "ball", "bat", "racquet", "shuttle", "hockey stick",
            "dumbbell", "treadmill", "yoga mat", "gym bag", "bicycle helmet", "tent", "sleeping bag",
            "passport", "boarding pass", "id card", "credit card", "money", "coin", "cash", "bill",
            "plant pot", "flower", "leaf", "tree", "rock", "brick", "tile", "wood log", "paint bucket",
            "paint brush", "canvas", "mirror", "curtain", "pillow", "bedsheet", "blanket", "mattress"
        )


        val results = mutableListOf<String>()
        for (detection in output) {
            val scores = detection.slice(4 until detection.size)
            val max = scores.maxOrNull() ?: 0f
            val classId = scores.indexOf(max)
            if (max > 0.5f) results.add(labels[classId])
        }
        return results.distinct()
    }
}

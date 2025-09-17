package com.example.theftdetector

import android.content.Context
import android.graphics.Bitmap
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.ImageProxy
import androidx.core.graphics.drawable.toBitmap
import org.tensorflow.lite.support.image.TensorImage

class CameraPreviewAnalyzer(
    private val context: Context,
    private val classifier: YoloClassifier,
    private val onResult: (List<String>) -> Unit
) : ImageAnalysis.Analyzer {

    private val yuvToRgbConverter = YuvToRgbConverter(context)

    override fun analyze(image: ImageProxy) {
        val bitmap = image.toBitmap() ?: run {
            image.close()
            return
        }

        val results = classifier.detect(bitmap)
        onResult(results)

        image.close()
    }

    private fun ImageProxy.toBitmap(): Bitmap? {
        val bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
        yuvToRgbConverter.yuvToRgb(this, bitmap)
        return bitmap
    }
}

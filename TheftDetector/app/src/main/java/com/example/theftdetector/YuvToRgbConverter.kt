package com.example.theftdetector

import android.content.Context
import android.graphics.Bitmap
import android.graphics.ImageFormat
import android.graphics.PixelFormat
import android.graphics.Rect
import android.graphics.YuvImage
import android.media.Image
import android.renderscript.*
import androidx.camera.core.ImageProxy
import java.io.ByteArrayOutputStream
import java.nio.ByteBuffer

class YuvToRgbConverter(context: Context) {

    private val rs: RenderScript = RenderScript.create(context)
    private val scriptYuvToRgb = ScriptIntrinsicYuvToRGB.create(rs, Element.U8_4(rs))

    fun yuvToRgb(image: ImageProxy, output: Bitmap) {
        val yuvBytes = yuv420ToNv21(image)
        val input = Allocation.createSized(rs, Element.U8(rs), yuvBytes.size)
        val outputAlloc = Allocation.createFromBitmap(rs, output)

        input.copyFrom(yuvBytes)
        scriptYuvToRgb.setInput(input)
        scriptYuvToRgb.forEach(outputAlloc)
        outputAlloc.copyTo(output)
    }

    private fun yuv420ToNv21(image: ImageProxy): ByteArray {
        val yBuffer = image.planes[0].buffer
        val uBuffer = image.planes[1].buffer
        val vBuffer = image.planes[2].buffer

        val ySize = yBuffer.remaining()
        val uSize = uBuffer.remaining()
        val vSize = vBuffer.remaining()

        val nv21 = ByteArray(ySize + uSize + vSize)
        yBuffer.get(nv21, 0, ySize)
        vBuffer.get(nv21, ySize, vSize)
        uBuffer.get(nv21, ySize + vSize, uSize)

        return nv21
    }
}

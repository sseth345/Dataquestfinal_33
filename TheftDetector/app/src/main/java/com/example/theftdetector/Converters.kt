package com.example.theftdetector

import android.graphics.RectF
import androidx.room.TypeConverter

class Converters {
    @TypeConverter
    fun fromRectF(rect: RectF): String = "${rect.left},${rect.top},${rect.right},${rect.bottom}"

    @TypeConverter
    fun toRectF(value: String): RectF {
        val parts = value.split(",")
        return RectF(
            parts[0].toFloat(),
            parts[1].toFloat(),
            parts[2].toFloat(),
            parts[3].toFloat()
        )
    }
}

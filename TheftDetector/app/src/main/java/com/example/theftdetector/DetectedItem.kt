package com.example.theftdetector
import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "detected_items")
data class DetectedItemEntity(
    @PrimaryKey(autoGenerate = true) val id: Int? = null,
    val label: String,
    val confidence: Float,
    val boundingBox: String,
    val isDangerous: Boolean = false,
    val timestamp: Long = System.currentTimeMillis()
)


package com.example.theftdetector

import androidx.room.*

@Dao
interface DetectedItemDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertItem(item: DetectedItemEntity)

    @Query("SELECT * FROM detected_items ORDER BY timestamp DESC")
    suspend fun getAll(): List<DetectedItemEntity>

    @Query("DELETE FROM detected_items")
    suspend fun clearAll()
}

package com.example.theftdetector

import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.google.gson.Gson
import kotlinx.coroutines.*
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.IOException
import kotlin.random.Random

// ================== Data Models ==================
data class APIResponse(
    val empid: String,
    val name: String,
    val prediction: Int,
    val status: String,
    val probability: Double? = null,
    val confidence_score: Double? = null
)

data class PredictionResult(
    val response: APIResponse,
    val apiType: String,
    val timestamp: Long
)

data class AdvancedAPIRequest(
    val empid: String,
    val name: String,
    val size: Double,
    val attachments: Int,
    val external_email: Int,
    val hour_sin: Double,
    val hour_cos: Double,
    val day_sin: Double,
    val day_cos: Double,
    val is_weekend: Int,
    val unusual_hour: Int,
    val large_email: Int,
    val has_attachments: Int,
    val size_deviation: Double,
    val hour_deviation: Double,
    val openness: Double,
    val conscientiousness: Double,
    val extraversion: Double,
    val agreeableness: Double,
    val neuroticism: Double
)

data class SimpleAPIRequest(
    val empid: String,
    val name: String,
    val num_logins: Int,
    val avg_login_hour: Double,
    val unique_pcs: Int,
    val num_files_accessed: Int,
    val num_files_to_removable_file: Int,
    val num_files_from_removable_file: Int,
    val unique_files_file: Int,
    val avg_content_length_file: Int,
    val num_emails_sent_email: Int,
    val avg_num_recipients_email: Int,
    val pct_emails_with_attachment_email: Double,
    val avg_content_length_email: Int,
    val avg_size_email: Double,
    val num_decoy_files_accessed_decoy: Int,
    val pct_decoy_files_accessed_decoy: Double,
    val num_device_events_decoy: Int,
    val num_connects_decoy: Int,
    val num_disconnects_decoy: Int,
    val unique_pcs_device_decoy: Int,
    val avg_filetree_length_decoy: Int,
    val num_http_requests_decoy: Int,
    val unique_urls_decoy: Int,
    val unique_pcs_http_decoy: Int,
    val avg_content_length_http_decoy: Int
)

// ================== Ultra Dark Color Scheme ==================
val ultraDarkScheme = darkColorScheme(
    primary = Color(0xFF6366F1), // Indigo
    onPrimary = Color(0xFFFFFFFF),
    primaryContainer = Color(0xFF1A1625),
    onPrimaryContainer = Color(0xFFC7D2FE),
    secondary = Color(0xFF8B5CF6), // Violet
    onSecondary = Color(0xFFFFFFFF),
    secondaryContainer = Color(0xFF1F1729),
    onSecondaryContainer = Color(0xFFDDD6FE),
    tertiary = Color(0xFF06B6D4), // Cyan
    onTertiary = Color(0xFFFFFFFF),
    tertiaryContainer = Color(0xFF0F1419),
    onTertiaryContainer = Color(0xFFA5F3FC),
    surface = Color(0xFF0A0A0A),
    onSurface = Color(0xFFF8FAFC),
    background = Color(0xFF000000),
    onBackground = Color(0xFFF1F5F9),
    surfaceVariant = Color(0xFF111111),
    onSurfaceVariant = Color(0xFFCBD5E1),
    error = Color(0xFFEF4444),
    onError = Color(0xFFFFFFFF),
    outline = Color(0xFF1F1F1F),
    outlineVariant = Color(0xFF0F0F0F)
)

// ================== Enhanced Stats Card ==================
@Composable
fun StatsCard(
    title: String,
    value: String,
    icon: ImageVector,
    color: Color,
    modifier: Modifier = Modifier
) {
    val infiniteTransition = rememberInfiniteTransition(label = "glow")
    val glowAlpha by infiniteTransition.animateFloat(
        initialValue = 0.3f,
        targetValue = 0.7f,
        animationSpec = infiniteRepeatable(
            animation = tween(durationMillis = 1500, easing = EaseInOutSine),
            repeatMode = RepeatMode.Reverse
        ), label = "glow_alpha"
    )

    Card(
        modifier = modifier
            .shadow(
                elevation = 16.dp,
                shape = RoundedCornerShape(18.dp),
                spotColor = color.copy(alpha = 0.4f)
            ),
        shape = RoundedCornerShape(18.dp),
        colors = CardDefaults.cardColors(
            containerColor = Color(0xFF0A0A0A)
        )
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(
                    brush = Brush.radialGradient(
                        colors = listOf(
                            color.copy(alpha = 0.08f),
                            Color.Transparent
                        ),
                        radius = 120f
                    )
                )
                .padding(18.dp)
        ) {
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {
                Box(
                    modifier = Modifier
                        .size(52.dp)
                        .background(
                            brush = Brush.radialGradient(
                                colors = listOf(
                                    color.copy(alpha = glowAlpha * 0.25f),
                                    color.copy(alpha = glowAlpha * 0.08f),
                                    Color.Transparent
                                )
                            ),
                            shape = CircleShape
                        ),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = icon,
                        contentDescription = null,
                        tint = color,
                        modifier = Modifier.size(26.dp)
                    )
                }

                Spacer(modifier = Modifier.height(10.dp))

                Text(
                    text = value,
                    fontSize = 22.sp,
                    fontWeight = FontWeight.Bold,
                    color = color
                )

                Spacer(modifier = Modifier.height(3.dp))

                Text(
                    text = title,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Medium,
                    color = Color.White.copy(alpha = 0.7f),
                    textAlign = TextAlign.Center
                )
            }
        }
    }
}

// ================== Ultra Dark Animated Background ==================
@Composable
fun UltraDarkAnimatedBackground() {
    val infiniteTransition = rememberInfiniteTransition(label = "background")

    val gradientOffset by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(durationMillis = 10000, easing = LinearEasing),
            repeatMode = RepeatMode.Reverse
        ), label = "gradient_offset"
    )

    val colorShift by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(durationMillis = 15000, easing = EaseInOutSine),
            repeatMode = RepeatMode.Reverse
        ), label = "color_shift"
    )

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black)
            .background(
                brush = Brush.radialGradient(
                    colors = listOf(
                        Color.Black,
                        Color(0xFF0A0A0A),
                        Color(0xFF111111).copy(alpha = 0.3f + colorShift * 0.1f),
                        Color(0xFF6366F1).copy(alpha = 0.01f + colorShift * 0.015f),
                        Color(0xFF8B5CF6).copy(alpha = 0.01f + gradientOffset * 0.015f),
                        Color.Black
                    ),
                    center = androidx.compose.ui.geometry.Offset(
                        x = 0.2f + gradientOffset * 0.6f,
                        y = 0.1f + colorShift * 0.8f
                    ),
                    radius = 1000f + gradientOffset * 300f
                )
            )
    )
}

// ================== Result Card Component ==================
@Composable
fun PredictionResultCard(result: PredictionResult) {
    val isThreat = result.response.status.lowercase() != "normal"
    val statusColor = if (isThreat) Color(0xFFEF4444) else Color(0xFF10B981)
    val modelColor = if (result.apiType.contains("Advanced")) Color(0xFF8B5CF6) else Color(0xFF06B6D4)

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .shadow(
                elevation = 20.dp,
                shape = RoundedCornerShape(18.dp),
                spotColor = statusColor.copy(alpha = 0.3f)
            ),
        shape = RoundedCornerShape(18.dp),
        colors = CardDefaults.cardColors(
            containerColor = Color(0xFF0A0A0A)
        )
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(
                    brush = Brush.horizontalGradient(
                        colors = listOf(
                            statusColor.copy(alpha = 0.05f),
                            modelColor.copy(alpha = 0.05f),
                            Color.Transparent
                        )
                    )
                )
        ) {
            Column(
                modifier = Modifier.padding(22.dp),
                verticalArrangement = Arrangement.spacedBy(18.dp)
            ) {
                // Header Row
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(14.dp)
                    ) {
                        Box(
                            modifier = Modifier
                                .size(52.dp)
                                .background(
                                    brush = Brush.radialGradient(
                                        colors = listOf(
                                            modelColor.copy(alpha = 0.2f),
                                            modelColor.copy(alpha = 0.05f),
                                            Color.Transparent
                                        )
                                    ),
                                    shape = CircleShape
                                ),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                imageVector = if (result.apiType.contains("Advanced"))
                                    Icons.Default.Psychology else Icons.Default.Computer,
                                contentDescription = null,
                                tint = modelColor,
                                modifier = Modifier.size(26.dp)
                            )
                        }

                        Column {
                            Text(
                                text = result.apiType,
                                fontWeight = FontWeight.Bold,
                                fontSize = 16.sp,
                                color = Color.White
                            )
                            Text(
                                text = "AI Detection Model",
                                fontSize = 12.sp,
                                fontWeight = FontWeight.Medium,
                                color = Color.White.copy(alpha = 0.6f)
                            )
                        }
                    }

                    Card(
                        colors = CardDefaults.cardColors(
                            containerColor = statusColor.copy(alpha = 0.1f)
                        ),
                        shape = RoundedCornerShape(20.dp)
                    ) {
                        Text(
                            text = result.response.status.uppercase(),
                            modifier = Modifier.padding(horizontal = 14.dp, vertical = 7.dp),
                            color = statusColor,
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }

                // User Information
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(18.dp)
                ) {
                    InfoChip(
                        label = "Employee",
                        value = result.response.name,
                        icon = Icons.Default.Person,
                        modifier = Modifier.weight(1f)
                    )
                    InfoChip(
                        label = "ID",
                        value = result.response.empid,
                        icon = Icons.Default.Badge,
                        modifier = Modifier.weight(1f)
                    )
                }

                // Metrics
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(18.dp)
                ) {
                    result.response.probability?.let {
                        InfoChip(
                            label = "Probability",
                            value = "${String.format("%.1f", it * 100)}%",
                            icon = Icons.Default.Analytics,
                            modifier = Modifier.weight(1f)
                        )
                    }
                    result.response.confidence_score?.let {
                        InfoChip(
                            label = "Confidence",
                            value = "${String.format("%.1f", it * 100)}%",
                            icon = Icons.Default.TrendingUp,
                            modifier = Modifier.weight(1f)
                        )
                    }
                }
            }
        }
    }
}

// ================== Info Chip Component ==================
@Composable
fun InfoChip(
    label: String,
    value: String,
    icon: ImageVector,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(
            containerColor = Color(0xFF111111)
        ),
        shape = RoundedCornerShape(14.dp)
    ) {
        Row(
            modifier = Modifier.padding(14.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = Color.White.copy(alpha = 0.7f),
                modifier = Modifier.size(18.dp)
            )
            Column {
                Text(
                    text = label,
                    fontSize = 10.sp,
                    fontWeight = FontWeight.Medium,
                    color = Color.White.copy(alpha = 0.6f)
                )
                Spacer(modifier = Modifier.height(2.dp))
                Text(
                    text = value,
                    fontSize = 13.sp,
                    fontWeight = FontWeight.SemiBold,
                    color = Color.White
                )
            }
        }
    }
}

// ================== Main Home Screen ==================
@Composable
fun HomeScreen(
    onLogout: () -> Unit,
    onGoToDashboard: () -> Unit
) {
    val coroutineScope = rememberCoroutineScope()
    var predictionResults by remember { mutableStateOf(listOf<PredictionResult>()) }
    var isFetching by remember { mutableStateOf(false) }

    val totalPredictions = predictionResults.size
    val threatDetected = predictionResults.count { it.response.status.lowercase() != "normal" }
    val safeUsers = totalPredictions - threatDetected

    MaterialTheme(colorScheme = ultraDarkScheme) {
        Box(modifier = Modifier.fillMaxSize()) {
            UltraDarkAnimatedBackground()

            // Extra dark overlay for maximum darkness
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(
                        brush = Brush.verticalGradient(
                            colors = listOf(
                                Color.Black.copy(alpha = 0.3f),
                                Color.Black.copy(alpha = 0.5f),
                                Color.Black.copy(alpha = 0.7f)
                            )
                        )
                    )
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(20.dp)
                ) {
                    // Enhanced Header with Action Buttons
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(20.dp),
                        colors = CardDefaults.cardColors(
                            containerColor = Color(0xFF0A0A0A)
                        )
                    ) {
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .background(
                                    brush = Brush.horizontalGradient(
                                        colors = listOf(
                                            Color(0xFF6366F1).copy(alpha = 0.08f),
                                            Color(0xFF8B5CF6).copy(alpha = 0.08f),
                                            Color(0xFF06B6D4).copy(alpha = 0.08f)
                                        )
                                    )
                                )
                                .padding(22.dp)
                        ) {
                            Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Column(
                                        verticalArrangement = Arrangement.spacedBy(6.dp)
                                    ) {
                                        Text(
                                            text = "Security Dashboard",
                                            fontSize = 23.sp,
                                            fontWeight = FontWeight.ExtraBold,
                                            color = Color.White
                                        )
                                        Text(
                                            text = "AI-Powered Threat Detection System",
                                            fontSize = 13.sp,
                                            fontWeight = FontWeight.Medium,
                                            color = Color.White.copy(alpha = 0.7f)
                                        )
                                    }
                                }

                                // Action Buttons Row
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                                ) {
                                    // Dashboard Button
                                    Button(
                                        onClick = onGoToDashboard,
                                        colors = ButtonDefaults.buttonColors(
                                            containerColor = Color(0xFF06B6D4).copy(alpha = 0.8f)
                                        ),
                                        shape = RoundedCornerShape(14.dp),
                                        modifier = Modifier.weight(1f),
                                        contentPadding = PaddingValues(vertical = 12.dp)
                                    ) {
                                        Icon(
                                            Icons.Default.Dashboard,
                                            contentDescription = "Dashboard",
                                            modifier = Modifier.size(18.dp),
                                            tint = Color.White
                                        )
                                        Spacer(modifier = Modifier.width(8.dp))
                                        Text(
                                            "Dashboard",
                                            fontSize = 14.sp,
                                            fontWeight = FontWeight.SemiBold,
                                            color = Color.White
                                        )
                                    }

                                    // Logout Button
                                    Button(
                                        onClick = onLogout,
                                        colors = ButtonDefaults.buttonColors(
                                            containerColor = Color(0xFFEF4444).copy(alpha = 0.8f)
                                        ),
                                        shape = RoundedCornerShape(14.dp),
                                        modifier = Modifier.weight(1f),
                                        contentPadding = PaddingValues(vertical = 12.dp)
                                    ) {
                                        Icon(
                                            Icons.Default.Logout,
                                            contentDescription = "Logout",
                                            modifier = Modifier.size(18.dp),
                                            tint = Color.White
                                        )
                                        Spacer(modifier = Modifier.width(8.dp))
                                        Text(
                                            "Logout",
                                            fontSize = 14.sp,
                                            fontWeight = FontWeight.SemiBold,
                                            color = Color.White
                                        )
                                    }
                                }
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(24.dp))

                    // Stats Cards Section
                    AnimatedVisibility(
                        visible = totalPredictions > 0,
                        enter = slideInVertically() + fadeIn()
                    ) {
                        Column {
                            Text(
                                text = "Security Overview",
                                fontSize = 18.sp,
                                fontWeight = FontWeight.Bold,
                                color = Color.White,
                                modifier = Modifier.padding(bottom = 14.dp)
                            )

                            LazyRow(
                                horizontalArrangement = Arrangement.spacedBy(14.dp),
                                contentPadding = PaddingValues(horizontal = 2.dp)
                            ) {
                                item {
                                    StatsCard(
                                        title = "Total Scans",
                                        value = totalPredictions.toString(),
                                        icon = Icons.Default.Security,
                                        color = Color(0xFF06B6D4),
                                        modifier = Modifier.size(125.dp)
                                    )
                                }
                                item {
                                    StatsCard(
                                        title = "Threats Detected",
                                        value = threatDetected.toString(),
                                        icon = Icons.Default.Warning,
                                        color = Color(0xFFEF4444),
                                        modifier = Modifier.size(125.dp)
                                    )
                                }
                                item {
                                    StatsCard(
                                        title = "Safe Users",
                                        value = safeUsers.toString(),
                                        icon = Icons.Default.CheckCircle,
                                        color = Color(0xFF10B981),
                                        modifier = Modifier.size(125.dp)
                                    )
                                }
                            }

                            Spacer(modifier = Modifier.height(24.dp))
                        }
                    }

                    // Enhanced Scan Button
                    Button(
                        onClick = {
                            isFetching = true
                            predictionResults = listOf()
                            coroutineScope.launch {
                                val randomNames = List(20) { "User${Random.nextInt(1000,9999)}" }
                                val results = randomNames.flatMap { name ->
                                    listOf(
                                        asyncPrediction(coroutineScope, name, "Advanced AI") { callAdvancedAPI(name) },
                                        asyncPrediction(coroutineScope, name, "Simple ML") { callSimpleAPI(name) }
                                    )
                                }.map { it.await() }

                                predictionResults = results
                                isFetching = false
                            }
                        },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(56.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = Color.Transparent),
                        shape = RoundedCornerShape(16.dp),
                        contentPadding = PaddingValues(0.dp)
                    ) {
                        Box(
                            modifier = Modifier
                                .fillMaxSize()
                                .background(
                                    brush = Brush.horizontalGradient(
                                        colors = listOf(
                                            Color(0xFF6366F1).copy(alpha = 0.9f),
                                            Color(0xFF8B5CF6).copy(alpha = 0.9f),
                                            Color(0xFFA855F7).copy(alpha = 0.9f)
                                        )
                                    ),
                                    shape = RoundedCornerShape(16.dp)
                                ),
                            contentAlignment = Alignment.Center
                        ) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(14.dp)
                            ) {
                                if (isFetching) {
                                    CircularProgressIndicator(
                                        color = Color.White,
                                        modifier = Modifier.size(22.dp),
                                        strokeWidth = 2.5.dp
                                    )
                                    Text(
                                        "Running Security Scan...",
                                        fontSize = 15.sp,
                                        fontWeight = FontWeight.SemiBold,
                                        color = Color.White
                                    )
                                } else {
                                    Icon(
                                        Icons.Default.Security,
                                        contentDescription = null,
                                        tint = Color.White,
                                        modifier = Modifier.size(22.dp)
                                    )
                                    Text(
                                        "Start Security Scan",
                                        fontSize = 15.sp,
                                        fontWeight = FontWeight.SemiBold,
                                        color = Color.White
                                    )
                                }
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(22.dp))

                    // Results Section
                    if (predictionResults.isNotEmpty()) {
                        Text(
                            text = "Scan Results",
                            fontSize = 18.sp,
                            fontWeight = FontWeight.Bold,
                            color = Color.White,
                            modifier = Modifier.padding(bottom = 14.dp)
                        )
                    }

                    LazyColumn(
                        verticalArrangement = Arrangement.spacedBy(13.dp),
                        modifier = Modifier.fillMaxSize()
                    ) {
                        items(predictionResults) { result ->
                            AnimatedVisibility(
                                visible = true,
                                enter = slideInVertically(
                                    initialOffsetY = { it },
                                    animationSpec = tween(300, easing = EaseOutCubic)
                                ) + fadeIn(animationSpec = tween(300))
                            ) {
                                PredictionResultCard(result = result)
                            }
                        }
                    }
                }
            }
        }
    }
}

// ================== Helper Functions ==================
fun asyncPrediction(
    scope: CoroutineScope,
    name: String,
    apiType: String,
    call: suspend () -> APIResponse
) = scope.async(Dispatchers.IO) {
    val response = try {
        call()
    } catch (e: Exception) {
        APIResponse(empid = "", name = "Error", prediction = -1, status = "Error")
    }
    PredictionResult(response, apiType, System.currentTimeMillis())
}

// ================== API Functions ==================
suspend fun callAdvancedAPI(userInput: String): APIResponse {
    val client = OkHttpClient()
    val gson = Gson()
    val requestData = AdvancedAPIRequest(
        empid = "EMP${Random.nextInt(1, 999)}",
        name = userInput,
        size = Random.nextDouble(100.0, 2000.0),
        attachments = Random.nextInt(0, 10),
        external_email = Random.nextInt(0, 2),
        hour_sin = Random.nextDouble(0.0, 1.0),
        hour_cos = Random.nextDouble(0.0, 1.0),
        day_sin = Random.nextDouble(0.0, 1.0),
        day_cos = Random.nextDouble(0.0, 1.0),
        is_weekend = Random.nextInt(0, 2),
        unusual_hour = Random.nextInt(0, 2),
        large_email = Random.nextInt(0, 2),
        has_attachments = Random.nextInt(0, 2),
        size_deviation = Random.nextDouble(0.0, 1.0),
        hour_deviation = Random.nextDouble(0.0, 1.0),
        openness = Random.nextDouble(0.0, 1.0),
        conscientiousness = Random.nextDouble(0.0, 1.0),
        extraversion = Random.nextDouble(0.0, 1.0),
        agreeableness = Random.nextDouble(0.0, 1.0),
        neuroticism = Random.nextDouble(0.0, 1.0)
    )
    val body = gson.toJson(requestData).toRequestBody("application/json".toMediaType())
    val request = Request.Builder()
        .url("https://dataquestfinal-33.onrender.com/predict_advanced")
        .post(body)
        .build()

    return try {
        client.newCall(request).execute().use { response ->
            val json = response.body?.string()
            gson.fromJson(json, APIResponse::class.java)
        }
    } catch (e: IOException) {
        APIResponse(empid = "", name = "Error", prediction = -1, status = "Error")
    }
}

suspend fun callSimpleAPI(userInput: String): APIResponse {
    val client = OkHttpClient()
    val gson = Gson()
    val requestData = SimpleAPIRequest(
        empid = "EMP${Random.nextInt(1, 999)}",
        name = userInput,
        num_logins = Random.nextInt(1, 50),
        avg_login_hour = Random.nextDouble(0.0, 24.0),
        unique_pcs = Random.nextInt(1, 10),
        num_files_accessed = Random.nextInt(0, 100),
        num_files_to_removable_file = Random.nextInt(0, 50),
        num_files_from_removable_file = Random.nextInt(0, 50),
        unique_files_file = Random.nextInt(1, 100),
        avg_content_length_file = Random.nextInt(100, 5000),
        num_emails_sent_email = Random.nextInt(0, 50),
        avg_num_recipients_email = Random.nextInt(1, 10),
        pct_emails_with_attachment_email = Random.nextDouble(0.0, 1.0),
        avg_content_length_email = Random.nextInt(50, 2000),
        avg_size_email = Random.nextDouble(0.0, 10.0),
        num_decoy_files_accessed_decoy = Random.nextInt(0, 5),
        pct_decoy_files_accessed_decoy = Random.nextDouble(0.0, 1.0),
        num_device_events_decoy = Random.nextInt(0, 20),
        num_connects_decoy = Random.nextInt(0, 10),
        num_disconnects_decoy = Random.nextInt(0, 10),
        unique_pcs_device_decoy = Random.nextInt(1, 5),
        avg_filetree_length_decoy = Random.nextInt(1, 20),
        num_http_requests_decoy = Random.nextInt(0, 50),
        unique_urls_decoy = Random.nextInt(1, 20),
        unique_pcs_http_decoy = Random.nextInt(1, 5),
        avg_content_length_http_decoy = Random.nextInt(50, 2000)
    )
    val body = gson.toJson(requestData).toRequestBody("application/json".toMediaType())
    val request = Request.Builder()
        .url("https://dataquestfinal-33.onrender.com/predict_simple")
        .post(body)
        .build()

    return try {
        client.newCall(request).execute().use { response ->
            val json = response.body?.string()
            gson.fromJson(json, APIResponse::class.java)
        }
    } catch (e: IOException) {
        APIResponse(empid = "", name = "Error", prediction = -1, status = "Error")
    }
}
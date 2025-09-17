package com.example.theftdetector.ui

import androidx.compose.animation.core.*
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.blur
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.draw.scale
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.*
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.drawIntoCanvas
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.theftdetector.R
import kotlin.math.cos
import kotlin.math.sin

@Composable
fun LoginScreen(
    onGoogleSignIn: () -> Unit,
    onGitHubSignIn: () -> Unit,
) {
    val context = LocalContext.current

    // Animation states
    val infiniteTransition = rememberInfiniteTransition(label = "rotation")
    val rotation by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 360f,
        animationSpec = infiniteRepeatable(
            animation = tween(25000, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ), label = "rotation"
    )

    val pulseAnimation = rememberInfiniteTransition(label = "pulse")
    val pulseScale by pulseAnimation.animateFloat(
        initialValue = 1f,
        targetValue = 1.08f,
        animationSpec = infiniteRepeatable(
            animation = tween(3000, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ), label = "pulse"
    )

    val glowAnimation = rememberInfiniteTransition(label = "glow")
    val glowIntensity by glowAnimation.animateFloat(
        initialValue = 0.3f,
        targetValue = 0.8f,
        animationSpec = infiniteRepeatable(
            animation = tween(4000, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ), label = "glow"
    )

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                brush = Brush.radialGradient(
                    colors = listOf(
                        Color(0xFF0B0B1F),
                        Color(0xFF0F0F2A),
                        Color(0xFF1A1A3A),
                        Color(0xFF000000)
                    ),
                    radius = 1200f
                )
            )
    ) {
        // Enhanced animated background
        AnimatedCyberBackground(rotation, glowIntensity)

        Column(
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally,
            modifier = Modifier
                .fillMaxSize()
                .padding(24.dp)
        ) {
            // Ultra-modern app icon with neural network design
            Box(
                contentAlignment = Alignment.Center
            ) {
                // Outer energy ring
                Box(
                    modifier = Modifier
                        .size(200.dp)
                        .rotate(rotation * 0.3f)
                        .clip(CircleShape)
                        .border(
                            width = 1.5.dp,
                            brush = Brush.sweepGradient(
                                colors = listOf(
                                    Color.Transparent,
                                    Color(0xFF00E5FF).copy(alpha = glowIntensity),
                                    Color.Transparent,
                                    Color(0xFF1DE9B6).copy(alpha = glowIntensity * 0.7f),
                                    Color.Transparent,
                                    Color(0xFF3F51B5).copy(alpha = glowIntensity * 0.5f)
                                )
                            ),
                            shape = CircleShape
                        )
                )

                // Middle neural glow
                Box(
                    modifier = Modifier
                        .size(170.dp)
                        .scale(pulseScale)
                        .clip(CircleShape)
                        .background(
                            brush = Brush.radialGradient(
                                colors = listOf(
                                    Color(0xFF00E5FF).copy(alpha = 0.4f * glowIntensity),
                                    Color(0xFF1DE9B6).copy(alpha = 0.2f * glowIntensity),
                                    Color(0xFF3F51B5).copy(alpha = 0.1f * glowIntensity),
                                    Color.Transparent
                                )
                            )
                        )
                )

                // Main icon with glassmorphism effect
                Card(
                    modifier = Modifier
                        .size(140.dp),
                    shape = CircleShape,
                    colors = CardDefaults.cardColors(
                        containerColor = Color.White.copy(alpha = 0.1f)
                    ),
                    elevation = CardDefaults.cardElevation(
                        defaultElevation = 20.dp
                    )
                ) {
                    Box(
                        modifier = Modifier
                            .fillMaxSize()
                            .background(
                                brush = Brush.radialGradient(
                                    colors = listOf(
                                        Color(0xFF00E5FF).copy(alpha = 0.3f),
                                        Color(0xFF1DE9B6).copy(alpha = 0.2f),
                                        Color(0xFF3F51B5).copy(alpha = 0.1f)
                                    )
                                )
                            ),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = Icons.Default.Security,
                            contentDescription = "App Icon",
                            modifier = Modifier.size(70.dp),
                            tint = Color.White
                        )
                    }
                }

                // Inner rotating elements
                Box(
                    modifier = Modifier
                        .size(90.dp)
                        .rotate(-rotation * 0.8f),
                    contentAlignment = Alignment.Center
                ) {
                    repeat(3) { index ->
                        val angle = index * 120f
                        Box(
                            modifier = Modifier
                                .offset(
                                    x = (cos(Math.toRadians(angle.toDouble())) * 30).toFloat().dp,
                                    y = (sin(Math.toRadians(angle.toDouble())) * 30).toFloat().dp

                                )
                                .size(6.dp)
                                .clip(CircleShape)
                                .background(Color(0xFF00E5FF).copy(alpha = glowIntensity))
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(50.dp))

            // Ultra-sleek app title with holographic effect
            Column(
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    text = "THREAT SHIELD",
                    style = MaterialTheme.typography.headlineLarge.copy(
                        fontSize = 34.sp,
                        letterSpacing = 4.sp,
                        shadow = Shadow(
                            color = Color(0xFF00E5FF).copy(alpha = 0.8f),
                            offset = Offset(0f, 0f),
                            blurRadius = 20f
                        )
                    ),
                    fontWeight = FontWeight.Black,
                    color = Color.White,
                    textAlign = TextAlign.Center
                )

                Text(
                    text = "AI • SECURITY • DEFENSE",
                    style = MaterialTheme.typography.bodyMedium.copy(
                        fontSize = 13.sp,
                        letterSpacing = 2.sp
                    ),
                    color = Color(0xFF00E5FF).copy(alpha = 0.8f),
                    textAlign = TextAlign.Center,
                    modifier = Modifier.padding(top = 4.dp)
                )
            }

            Spacer(modifier = Modifier.height(30.dp))

            // Futuristic description
            Text(
                text = "Machine Learning Powered • Real-time Threat Detection • Neural Network Defense",
                style = MaterialTheme.typography.bodyMedium.copy(
                    fontSize = 14.sp,
                    letterSpacing = 0.8.sp
                ),
                color = Color(0xFFB0BEC5).copy(alpha = 0.9f),
                textAlign = TextAlign.Center,
                modifier = Modifier.padding(horizontal = 20.dp)
            )

            Spacer(modifier = Modifier.height(60.dp))

            // Ultra-modern glassmorphism auth container
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 4.dp),
                shape = RoundedCornerShape(28.dp),
                colors = CardDefaults.cardColors(
                    containerColor = Color.White.copy(alpha = 0.05f)
                ),
                elevation = CardDefaults.cardElevation(
                    defaultElevation = 25.dp
                )
            ) {
                Column(
                    modifier = Modifier
                        .background(
                            brush = Brush.verticalGradient(
                                colors = listOf(
                                    Color.White.copy(alpha = 0.1f),
                                    Color.White.copy(alpha = 0.05f)
                                )
                            )
                        )
                        .border(
                            width = 1.dp,
                            brush = Brush.verticalGradient(
                                colors = listOf(
                                    Color.White.copy(alpha = 0.2f),
                                    Color.Transparent
                                )
                            ),
                            shape = RoundedCornerShape(28.dp)
                        )
                        .padding(32.dp),
                    verticalArrangement = Arrangement.spacedBy(24.dp)
                ) {
                    // Auth header with cyber styling
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.Center,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Box(
                            modifier = Modifier
                                .size(8.dp)
                                .clip(CircleShape)
                                .background(Color(0xFF00E5FF))
                        )
                        Spacer(modifier = Modifier.width(12.dp))
                        Text(
                            text = "SECURE ACCESS PORTAL",
                            style = MaterialTheme.typography.titleMedium.copy(
                                fontSize = 16.sp,
                                letterSpacing = 1.5.sp
                            ),
                            color = Color.White.copy(alpha = 0.9f),
                            fontWeight = FontWeight.Bold
                        )
                        Spacer(modifier = Modifier.width(12.dp))
                        Box(
                            modifier = Modifier
                                .size(8.dp)
                                .clip(CircleShape)
                                .background(Color(0xFF1DE9B6))
                        )
                    }

                    // Ultra-sleek Google button
                    Card(
                        onClick = onGoogleSignIn,
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(58.dp),
                        shape = RoundedCornerShape(22.dp),
                        colors = CardDefaults.cardColors(
                            containerColor = Color.White
                        ),
                        elevation = CardDefaults.cardElevation(
                            defaultElevation = 12.dp,
                            pressedElevation = 8.dp,
                            hoveredElevation = 16.dp
                        )
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.Center,
                            modifier = Modifier.fillMaxSize()
                        ) {
                            Box(
                                modifier = Modifier
                                    .size(40.dp)
                                    .clip(CircleShape)
                                    .background(
                                        brush = Brush.radialGradient(
                                            colors = listOf(
                                                Color(0xFF4285F4),
                                                Color(0xFF34A853),
                                                Color(0xFFEA4335),
                                                Color(0xFFFBBC05)
                                            )
                                        )
                                    ),
                                contentAlignment = Alignment.Center
                            ) {
                                Text(
                                    text = "G",
                                    fontSize = 20.sp,
                                    fontWeight = FontWeight.ExtraBold,
                                    color = Color.White
                                )
                            }
                            Spacer(modifier = Modifier.width(16.dp))
                            Text(
                                text = "Continue with Google",
                                fontSize = 17.sp,
                                fontWeight = FontWeight.SemiBold,
                                color = Color(0xFF1F1F1F)
                            )
                        }
                    }

                    // Ultra-sleek GitHub button
                    Card(
                        onClick = onGitHubSignIn,
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(68.dp),
                        shape = RoundedCornerShape(22.dp),
                        colors = CardDefaults.cardColors(
                            containerColor = Color(0xFF0D1117)
                        ),
                        elevation = CardDefaults.cardElevation(
                            defaultElevation = 12.dp,
                            pressedElevation = 8.dp,
                            hoveredElevation = 16.dp
                        )
                    ) {
                        Box(
                            modifier = Modifier
                                .fillMaxSize()
                                .background(
                                    brush = Brush.horizontalGradient(
                                        colors = listOf(
                                            Color(0xFF0D1117),
                                            Color(0xFF161B22),
                                            Color(0xFF0D1117)
                                        )
                                    )
                                )
                                .border(
                                    width = 1.dp,
                                    color = Color(0xFF30363D),
                                    shape = RoundedCornerShape(22.dp)
                                )
                        ) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.Center,
                                modifier = Modifier.fillMaxSize()
                            ) {
                                Box(
                                    modifier = Modifier
                                        .size(40.dp)
                                        .clip(CircleShape)
                                        .background(Color.White),
                                    contentAlignment = Alignment.Center
                                ) {
                                    Icon(
                                        imageVector = Icons.Default.Code,
                                        contentDescription = "GitHub",
                                        modifier = Modifier.size(22.dp),
                                        tint = Color(0xFF0D1117)
                                    )
                                }
                                Spacer(modifier = Modifier.width(16.dp))
                                Text(
                                    text = "Continue with GitHub",
                                    fontSize = 17.sp,
                                    fontWeight = FontWeight.SemiBold,
                                    color = Color.White
                                )
                            }
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(50.dp))

            // Enhanced security features with neural styling
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(32.dp),
                modifier = Modifier.padding(horizontal = 20.dp)
            ) {
                CyberSecurityFeature(Icons.Default.Psychology, "AI Powered", Color(0xFF00E5FF))
                CyberSecurityFeature(Icons.Default.Shield, "Neural Guard", Color(0xFF1DE9B6))
                CyberSecurityFeature(Icons.Default.Speed, "Real-time", Color(0xFF3F51B5))
            }
        }

        // Floating neural network nodes
        repeat(8) { index ->
            val angle = (rotation * 0.5f + index * 45f) * (kotlin.math.PI / 180f)
            val radius = 180f + index * 25f
            val x = (kotlin.math.cos(angle) * radius).toFloat()
            val y = (kotlin.math.sin(angle) * radius).toFloat()

            Box(
                modifier = Modifier
                    .offset(
                        x = x.dp,
                        y = y.dp
                    )
                    .size((12 - index).dp)
                    .clip(CircleShape)
                    .background(
                        when (index % 3) {
                            0 -> Color(0xFF00E5FF).copy(alpha = 0.3f - index * 0.03f)
                            1 -> Color(0xFF1DE9B6).copy(alpha = 0.25f - index * 0.02f)
                            else -> Color(0xFF3F51B5).copy(alpha = 0.2f - index * 0.02f)
                        }
                    )
            )
        }
    }
}

@Composable
fun CyberSecurityFeature(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    text: String,
    accentColor: Color
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        Card(
            modifier = Modifier.size(48.dp),
            shape = CircleShape,
            colors = CardDefaults.cardColors(
                containerColor = accentColor.copy(alpha = 0.15f)
            ),
            elevation = CardDefaults.cardElevation(
                defaultElevation = 8.dp
            )
        ) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(
                        brush = Brush.radialGradient(
                            colors = listOf(
                                accentColor.copy(alpha = 0.3f),
                                accentColor.copy(alpha = 0.1f),
                                Color.Transparent
                            )
                        )
                    ),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = text,
                    modifier = Modifier.size(24.dp),
                    tint = accentColor
                )
            }
        }
        Text(
            text = text,
            style = MaterialTheme.typography.bodySmall.copy(
                fontSize = 11.sp,
                letterSpacing = 0.8.sp
            ),
            color = Color.White.copy(alpha = 0.8f),
            fontWeight = FontWeight.SemiBold,
            textAlign = TextAlign.Center
        )
    }
}

@Composable
fun AnimatedCyberBackground(rotation: Float, glowIntensity: Float) {
    Canvas(
        modifier = Modifier.fillMaxSize()
    ) {
        val width = size.width
        val height = size.height
        val centerX = width / 2
        val centerY = height / 2

        // Neural network grid
        for (i in 0..15) {
            val alpha = (0.15f - i * 0.008f) * glowIntensity
            val radius = i * 60f + (rotation * 1.5f) % 120f

            drawCircle(
                color = Color(0xFF00E5FF).copy(alpha = alpha),
                radius = radius,
                center = Offset(centerX, centerY),
                style = Stroke(width = 0.8.dp.toPx())
            )
        }

        // Data flow lines
        for (angle in 0..360 step 30) {
            val radian = (angle + rotation * 0.3f) * (kotlin.math.PI / 180f)
            val startRadius = 80f
            val endRadius = 400f

            val startX = centerX + cos(radian).toFloat() * startRadius
            val startY = centerY + sin(radian).toFloat() * startRadius
            val endX = centerX + cos(radian).toFloat() * endRadius
            val endY = centerY + sin(radian).toFloat() * endRadius

            drawLine(
                brush = Brush.linearGradient(
                    colors = listOf(
                        Color(0xFF1DE9B6).copy(alpha = 0.2f * glowIntensity),
                        Color.Transparent
                    )
                ),
                start = Offset(startX, startY),
                end = Offset(endX, endY),
                strokeWidth = 1.dp.toPx()
            )
        }

        // Hex pattern overlay
        val hexSize = 100f
        for (x in 0..6) {
            for (y in 0..10) {
                val hexX = x * hexSize * 0.75f
                val hexY = y * hexSize * 0.9f + (x % 2) * hexSize * 0.45f

                drawCircle(
                    color = Color(0xFF3F51B5).copy(alpha = 0.05f * glowIntensity),
                    radius = 30f,
                    center = Offset(hexX, hexY),
                    style = Stroke(width = 0.5.dp.toPx())
                )
            }
        }
    }
}
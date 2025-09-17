package com.example.theftdetector

import android.content.Context
import android.widget.Toast
import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
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
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import java.io.File
import java.io.FileWriter
import java.text.SimpleDateFormat
import java.util.*
import kotlin.random.Random

// Enhanced Color Palette
private val BlackBg = Color(0xFF0A0A0A)
private val DarkCard = Color(0xFF1A1A1A)
private val DarkerCard = Color(0xFF141414)
private val GreenAccent = Color(0xFF00FF88)
private val BlueAccent = Color(0xFF0099FF)
private val PurpleAccent = Color(0xFF8B5CF6)
private val RedAlert = Color(0xFFFF4757)
private val OrangeWarn = Color(0xFFFF6B35)
private val YellowWarn = Color(0xFFFFD93D)
private val WhiteText = Color(0xFFFFFFFF)
private val GrayText = Color(0xFF8A8A8A)
private val LightGray = Color(0xFFB8B8B8)

// Gradient Colors
private val GreenGradient = Brush.horizontalGradient(
    colors = listOf(GreenAccent.copy(alpha = 0.8f), GreenAccent.copy(alpha = 0.3f))
)
private val BlueGradient = Brush.horizontalGradient(
    colors = listOf(BlueAccent.copy(alpha = 0.8f), BlueAccent.copy(alpha = 0.3f))
)
private val RedGradient = Brush.horizontalGradient(
    colors = listOf(RedAlert.copy(alpha = 0.8f), RedAlert.copy(alpha = 0.3f))
)
private val PurpleGradient = Brush.horizontalGradient(
    colors = listOf(PurpleAccent.copy(alpha = 0.8f), PurpleAccent.copy(alpha = 0.3f))
)

// Data Classes (same as before)
data class SimpleMetrics(
    val activeThreats: Int,
    val systemsOnline: Int,
    val securityLevel: String,
    val lastScan: String,
    val employeesMonitored: Int,
    val normalBehavior: Int,
    val suspiciousActivity: Int
)

data class SimpleIncident(
    val id: Int,
    val title: String,
    val severity: String,
    val location: String,
    val time: String,
    val status: String,
    val empId: String,
    val empName: String
)

data class EmployeeData(
    val empId: String,
    val name: String,
    val prediction: Int,
    val status: String,
    val confidenceScore: Double,
    val location: String,
    val timestamp: String
)

// Sample Data Functions (same as before)
fun generateSimpleData(): SimpleMetrics {
    val suspicious = Random.nextInt(0, 8)
    val normal = Random.nextInt(45, 95)
    return SimpleMetrics(
        activeThreats = Random.nextInt(0, 5),
        systemsOnline = Random.nextInt(85, 100),
        securityLevel = listOf("SECURE", "MODERATE", "HIGH ALERT").random(),
        lastScan = "Live",
        employeesMonitored = normal + suspicious,
        normalBehavior = normal,
        suspiciousActivity = suspicious
    )
}

fun getSimpleIncidents(): List<SimpleIncident> {
    return listOf(
        SimpleIncident(1, "Unauthorized Access Detected", "HIGH", "Server Room Alpha", "Live", "ACTIVE", "EMP001", "Shreyash Kumar"),
        SimpleIncident(2, "Suspicious Behavioral Pattern", "MEDIUM", "Floor 2 East Wing", "2 min ago", "MONITORING", "EMP045", "Priya Sharma"),
        SimpleIncident(3, "Unusual Access Time", "LOW", "Main Entrance", "15 min ago", "RESOLVED", "EMP078", "Rahul Singh"),
        SimpleIncident(4, "Data Transfer Anomaly", "HIGH", "Network Hub", "8 min ago", "INVESTIGATING", "EMP023", "Anita Verma")
    )
}

fun generateEmployeeData(): List<EmployeeData> {
    val names = listOf(
        "Shreyash Kumar", "Priya Sharma", "Rahul Singh", "Anita Verma", "Vikram Gupta",
        "Sneha Patel", "Arjun Reddy", "Kavya Nair", "Sanjay Yadav", "Pooja Joshi",
        "Rohan Mehta", "Deepika Shah", "Amit Agarwal", "Ritu Bansal", "Karan Malhotra"
    )

    val locations = listOf(
        "Executive Floor", "Development Wing", "Marketing Hub", "Finance Sector", "Cafeteria Zone",
        "Parking Level B1", "Reception Lobby", "Conference Suite", "Server Farm", "R&D Lab"
    )

    return names.mapIndexed { index, name ->
        val prediction = if (Random.nextFloat() < 0.15f) 1 else 0
        val confidence = if (prediction == 1) {
            Random.nextDouble(0.6, 0.95)
        } else {
            Random.nextDouble(0.02, 0.3)
        }

        EmployeeData(
            empId = "EMP${String.format("%03d", index + 1)}",
            name = name,
            prediction = prediction,
            status = if (prediction == 1) "FLAGGED" else "NORMAL",
            confidenceScore = confidence,
            location = locations.random(),
            timestamp = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault())
                .format(System.currentTimeMillis() - Random.nextLong(0, 3600000))
        )
    }
}

// CSV Export Function (same as before)
fun exportToCSV(
    context: Context,
    metrics: SimpleMetrics,
    incidents: List<SimpleIncident>,
    employees: List<EmployeeData>
) {
    try {
        val timeStamp = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(Date())
        val csvFile = File(context.getExternalFilesDir(null), "security_report_$timeStamp.csv")
        val writer = FileWriter(csvFile)

        writer.append("=== SECURITY DASHBOARD REPORT ===\n")
        writer.append("Generated On,${SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault()).format(Date())}\n")
        writer.append("Security Level,${metrics.securityLevel}\n")
        writer.append("Active Threats,${metrics.activeThreats}\n")
        writer.append("Systems Online,${metrics.systemsOnline}%\n")
        writer.append("Employees Monitored,${metrics.employeesMonitored}\n")
        writer.append("Normal Behavior,${metrics.normalBehavior}\n")
        writer.append("Suspicious Activity,${metrics.suspiciousActivity}\n\n")

        writer.append("=== SECURITY INCIDENTS ===\n")
        writer.append("ID,Title,Severity,Location,Time,Status,Employee ID,Employee Name\n")
        incidents.forEach { incident ->
            writer.append("${incident.id},\"${incident.title}\",${incident.severity},\"${incident.location}\",\"${incident.time}\",${incident.status},${incident.empId},\"${incident.empName}\"\n")
        }

        writer.append("\n=== EMPLOYEE MONITORING DATA ===\n")
        writer.append("Employee ID,Name,Prediction,Status,Confidence Score,Location,Timestamp\n")
        employees.forEach { emp ->
            writer.append("${emp.empId},\"${emp.name}\",${emp.prediction},${emp.status},${emp.confidenceScore},\"${emp.location}\",\"${emp.timestamp}\"\n")
        }

        writer.flush()
        writer.close()

        Toast.makeText(context, "✅ Security Report Exported Successfully!\n📁 ${csvFile.name}", Toast.LENGTH_LONG).show()

    } catch (e: Exception) {
        Toast.makeText(context, "❌ Export Failed: ${e.message}", Toast.LENGTH_SHORT).show()
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DashboardScreen(onBack: () -> Unit) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()

    var metrics by remember { mutableStateOf(generateSimpleData()) }
    val incidents = remember { getSimpleIncidents() }
    val employees = remember { generateEmployeeData() }
    var selectedTab by remember { mutableStateOf(0) }

    // Enhanced auto-refresh with animation
    LaunchedEffect(Unit) {
        while (true) {
            kotlinx.coroutines.delay(12000)
            metrics = generateSimpleData()
        }
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                Brush.radialGradient(
                    colors = listOf(
                        BlackBg,
                        Color(0xFF0F0F0F),
                        Color(0xFF050505)
                    ),
                    radius = 1200f
                )
            )
    ) {
        Column(
            modifier = Modifier.fillMaxSize()
        ) {
            // Premium Header
            PremiumHeader(
                onBack = onBack,
                onDownload = {
                    coroutineScope.launch(Dispatchers.IO) {
                        exportToCSV(context, metrics, incidents, employees)
                    }
                },
                metrics = metrics
            )

            Spacer(modifier = Modifier.height(8.dp))

            // Main Content with enhanced scrolling
            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                item {
                    AnimatedStatsGrid(metrics = metrics)
                }

                item {
                    PremiumTabSelector(
                        selectedTab = selectedTab,
                        onTabSelected = { selectedTab = it }
                    )
                }

                item {
                    AnimatedVisibility(
                        visible = true,
                        enter = slideInVertically() + fadeIn(),
                        exit = slideOutVertically() + fadeOut()
                    ) {
                        when (selectedTab) {
                            0 -> EnhancedOverviewSection(metrics = metrics)
                            1 -> PremiumIncidentsList(incidents = incidents)
                            2 -> AdvancedEmployeeMonitoring(employees = employees)
                            3 -> ModernSystemStatus(metrics = metrics)
                        }
                    }
                }

                // Bottom spacing
                item {
                    Spacer(modifier = Modifier.height(100.dp))
                }
            }
        }

        // Floating Action Elements
        FloatingElements()
    }
}

@Composable
fun PremiumHeader(
    onBack: () -> Unit,
    onDownload: () -> Unit,
    metrics: SimpleMetrics
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        shape = RoundedCornerShape(24.dp),
        colors = CardDefaults.cardColors(
            containerColor = DarkCard.copy(alpha = 0.95f)
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 8.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .background(
                    Brush.linearGradient(
                        colors = listOf(
                            DarkCard.copy(alpha = 0.9f),
                            DarkerCard.copy(alpha = 0.8f)
                        )
                    )
                )
                .padding(20.dp)
        ) {
            // Top Row
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Enhanced Back Button
                IconButton(
                    onClick = onBack,
                    modifier = Modifier
                        .size(48.dp)
                        .background(
                            Brush.radialGradient(
                                colors = listOf(BlueAccent, BlueAccent.copy(alpha = 0.7f))
                            ),
                            CircleShape
                        )
                        .border(2.dp, BlueAccent.copy(alpha = 0.3f), CircleShape)
                ) {
                    Icon(
                        Icons.Default.ArrowBack,
                        contentDescription = "Back",
                        tint = Color.White,
                        modifier = Modifier.size(20.dp)
                    )
                }

                // Enhanced Download Button
                IconButton(
                    onClick = onDownload,
                    modifier = Modifier
                        .size(48.dp)
                        .background(
                            Brush.radialGradient(
                                colors = listOf(GreenAccent, GreenAccent.copy(alpha = 0.7f))
                            ),
                            CircleShape
                        )
                        .border(2.dp, GreenAccent.copy(alpha = 0.3f), CircleShape)
                ) {
                    Icon(
                        Icons.Default.Download,
                        contentDescription = "Export Data",
                        tint = Color.White,
                        modifier = Modifier.size(20.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            // Title Section
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.Center,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier
                        .size(12.dp)
                        .background(GreenAccent, CircleShape)
                )

                Spacer(modifier = Modifier.width(8.dp))

                Text(
                    "SECURITY COMMAND CENTER",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.ExtraBold,
                    color = WhiteText,
                    letterSpacing = 1.2.sp
                )

                Spacer(modifier = Modifier.width(8.dp))

                Box(
                    modifier = Modifier
                        .size(12.dp)
                        .background(GreenAccent, CircleShape)
                )
            }

            Spacer(modifier = Modifier.height(8.dp))

            // Status Line
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.Center
            ) {
                val statusColor = when (metrics.securityLevel) {
                    "SECURE" -> GreenAccent
                    "MODERATE" -> YellowWarn
                    else -> RedAlert
                }

                Text(
                    "● ${metrics.securityLevel} ● LIVE MONITORING ●",
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Bold,
                    color = statusColor,
                    letterSpacing = 0.8.sp
                )
            }
        }
    }
}

@Composable
fun AnimatedStatsGrid(metrics: SimpleMetrics) {
    val infiniteTransition = rememberInfiniteTransition(label = "stats")
    val pulse by infiniteTransition.animateFloat(
        initialValue = 0.95f,
        targetValue = 1.05f,
        animationSpec = infiniteRepeatable(
            animation = tween(2000, easing = EaseInOutSine),
            repeatMode = RepeatMode.Reverse
        ), label = "pulse"
    )

    Column(
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        // Top Row
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            PremiumStatCard(
                title = "Active Threats",
                value = metrics.activeThreats.toString(),
                gradient = if (metrics.activeThreats > 0) RedGradient else GreenGradient,
                icon = Icons.Default.Warning,
                iconColor = if (metrics.activeThreats > 0) RedAlert else GreenAccent,
                modifier = Modifier
                    .weight(1f)
                    .scale(if (metrics.activeThreats > 0) pulse else 1f)
            )

            PremiumStatCard(
                title = "Systems Online",
                value = "${metrics.systemsOnline}%",
                gradient = if (metrics.systemsOnline > 90) GreenGradient else Brush.horizontalGradient(
                    colors = listOf(OrangeWarn.copy(alpha = 0.8f), OrangeWarn.copy(alpha = 0.3f))
                ),
                icon = Icons.Default.Computer,
                iconColor = if (metrics.systemsOnline > 90) GreenAccent else OrangeWarn,
                modifier = Modifier.weight(1f)
            )
        }

        // Bottom Row
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            PremiumStatCard(
                title = "Normal Users",
                value = metrics.normalBehavior.toString(),
                gradient = BlueGradient,
                icon = Icons.Default.CheckCircle,
                iconColor = BlueAccent,
                modifier = Modifier.weight(1f)
            )

            PremiumStatCard(
                title = "Flagged Users",
                value = metrics.suspiciousActivity.toString(),
                gradient = if (metrics.suspiciousActivity > 0) Brush.horizontalGradient(
                    colors = listOf(OrangeWarn.copy(alpha = 0.8f), OrangeWarn.copy(alpha = 0.3f))
                ) else GreenGradient,
                icon = Icons.Default.RemoveRedEye,
                iconColor = if (metrics.suspiciousActivity > 0) OrangeWarn else GreenAccent,
                modifier = Modifier
                    .weight(1f)
                    .scale(if (metrics.suspiciousActivity > 0) pulse else 1f)
            )
        }
    }
}

@Composable
fun PremiumStatCard(
    title: String,
    value: String,
    gradient: Brush,
    icon: ImageVector,
    iconColor: Color,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.height(120.dp),
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(containerColor = DarkCard),
        elevation = CardDefaults.cardElevation(defaultElevation = 6.dp)
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(gradient)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(16.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.SpaceEvenly
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = title,
                    tint = iconColor,
                    modifier = Modifier.size(32.dp)
                )

                Text(
                    text = value,
                    fontSize = 24.sp,
                    fontWeight = FontWeight.ExtraBold,
                    color = WhiteText
                )

                Text(
                    text = title,
                    fontSize = 11.sp,
                    color = LightGray,
                    textAlign = TextAlign.Center,
                    fontWeight = FontWeight.Medium,
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis
                )
            }
        }
    }
}

@Composable
fun PremiumTabSelector(
    selectedTab: Int,
    onTabSelected: (Int) -> Unit
) {
    val tabs = listOf(
        "Overview" to Icons.Default.Dashboard,
        "Incidents" to Icons.Default.Warning,
        "Employees" to Icons.Default.People,
        "Status" to Icons.Default.Settings
    )

    LazyRow(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        contentPadding = PaddingValues(horizontal = 4.dp)
    ) {
        items(tabs.size) { index ->
            val (tabName, tabIcon) = tabs[index]
            val isSelected = selectedTab == index

            Card(
                modifier = Modifier
                    .clickable { onTabSelected(index) }
                    .animateContentSize(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(
                    containerColor = if (isSelected) BlueAccent else DarkCard
                ),
                elevation = CardDefaults.cardElevation(
                    defaultElevation = if (isSelected) 8.dp else 2.dp
                )
            ) {
                Row(
                    modifier = Modifier.padding(
                        horizontal = if (isSelected) 20.dp else 16.dp,
                        vertical = 12.dp
                    ),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Icon(
                        imageVector = tabIcon,
                        contentDescription = tabName,
                        tint = if (isSelected) Color.White else LightGray,
                        modifier = Modifier.size(20.dp)
                    )

                    if (isSelected) {
                        Text(
                            text = tabName,
                            color = Color.White,
                            fontWeight = FontWeight.Bold,
                            fontSize = 14.sp
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun EnhancedOverviewSection(metrics: SimpleMetrics) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(24.dp),
        colors = CardDefaults.cardColors(containerColor = DarkCard),
        elevation = CardDefaults.cardElevation(defaultElevation = 8.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .background(
                    Brush.verticalGradient(
                        colors = listOf(
                            DarkCard,
                            DarkerCard
                        )
                    )
                )
                .padding(28.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(24.dp)
        ) {
            // Main Status Icon
            val rotation by rememberInfiniteTransition(label = "rotation").animateFloat(
                initialValue = 0f,
                targetValue = 360f,
                animationSpec = infiniteRepeatable(
                    animation = tween(20000, easing = LinearEasing),
                    repeatMode = RepeatMode.Restart
                ), label = "rotation"
            )

            Box(
                contentAlignment = Alignment.Center
            ) {
                // Outer ring
                Box(
                    modifier = Modifier
                        .size(120.dp)
                        .rotate(rotation)
                        .border(
                            width = 3.dp,
                            brush = Brush.sweepGradient(
                                colors = listOf(
                                    BlueAccent,
                                    GreenAccent,
                                    PurpleAccent,
                                    BlueAccent
                                )
                            ),
                            shape = CircleShape
                        )
                )

                // Inner content
                Box(
                    modifier = Modifier
                        .size(80.dp)
                        .background(
                            if (metrics.activeThreats == 0) GreenAccent else OrangeWarn,
                            CircleShape
                        ),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        Icons.Default.Shield,
                        contentDescription = "Security Status",
                        tint = Color.White,
                        modifier = Modifier.size(40.dp)
                    )
                }
            }

            // Status Text
            Text(
                text = if (metrics.activeThreats == 0) "SYSTEM SECURE" else "MONITORING ACTIVE",
                fontSize = 22.sp,
                fontWeight = FontWeight.ExtraBold,
                color = if (metrics.activeThreats == 0) GreenAccent else OrangeWarn,
                letterSpacing = 1.sp
            )

            // Details
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Text(
                    "Monitoring ${metrics.employeesMonitored} employees across all zones",
                    fontSize = 16.sp,
                    color = LightGray,
                    textAlign = TextAlign.Center
                )

                Row(
                    horizontalArrangement = Arrangement.spacedBy(24.dp)
                ) {
                    StatusIndicator("✅ ${metrics.normalBehavior} Normal", GreenAccent)
                    if (metrics.suspiciousActivity > 0) {
                        StatusIndicator("⚠️ ${metrics.suspiciousActivity} Flagged", OrangeWarn)
                    }
                }
            }

            // System Status Row
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                SystemIndicator("AI Engine", GreenAccent, true)
                SystemIndicator("Network", BlueAccent, true)
                SystemIndicator("Database", GreenAccent, true)
                SystemIndicator("Analytics", if (metrics.suspiciousActivity > 0) OrangeWarn else GreenAccent, true)
            }
        }
    }
}

@Composable
fun SystemIndicator(label: String, color: Color, isOnline: Boolean) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(6.dp)
    ) {
        Box(
            modifier = Modifier
                .size(14.dp)
                .background(
                    if (isOnline) color else GrayText,
                    CircleShape
                )
        )
        Text(
            label,
            fontSize = 10.sp,
            color = if (isOnline) color else GrayText,
            textAlign = TextAlign.Center,
            fontWeight = FontWeight.Medium
        )
    }
}

@Composable
fun StatusIndicator(text: String, color: Color) {
    Text(
        text = text,
        fontSize = 14.sp,
        color = color,
        fontWeight = FontWeight.Bold
    )
}

@Composable
fun PremiumIncidentsList(incidents: List<SimpleIncident>) {
    Column(
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        incidents.forEach { incident ->
            PremiumIncidentCard(incident = incident)
        }
    }
}

@Composable
fun PremiumIncidentCard(incident: SimpleIncident) {
    val severityColor = when (incident.severity) {
        "HIGH" -> RedAlert
        "MEDIUM" -> OrangeWarn
        "LOW" -> YellowWarn
        else -> BlueAccent
    }

    val statusColor = when (incident.status) {
        "ACTIVE" -> RedAlert
        "MONITORING", "INVESTIGATING" -> OrangeWarn
        "RESOLVED" -> GreenAccent
        else -> BlueAccent
    }

    val severityGradient = when (incident.severity) {
        "HIGH" -> RedGradient
        "MEDIUM" -> Brush.horizontalGradient(
            colors = listOf(OrangeWarn.copy(alpha = 0.8f), OrangeWarn.copy(alpha = 0.3f))
        )
        else -> Brush.horizontalGradient(
            colors = listOf(YellowWarn.copy(alpha = 0.8f), YellowWarn.copy(alpha = 0.3f))
        )
    }

    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(containerColor = DarkCard),
        elevation = CardDefaults.cardElevation(defaultElevation = 6.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .background(Color(0xFF4CAF50).copy(alpha = 0.1f))
                .padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp)
        ) {
            // Header Row
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        incident.title,
                        fontSize = 17.sp,
                        fontWeight = FontWeight.Bold,
                        color = WhiteText,
                        maxLines = 2,
                        overflow = TextOverflow.Ellipsis
                    )

                    Spacer(modifier = Modifier.height(4.dp))

                    Text(
                        "🚨 ${incident.severity} PRIORITY",
                        fontSize = 12.sp,
                        fontWeight = FontWeight.ExtraBold,
                        color = severityColor,
                        letterSpacing = 0.5.sp
                    )
                }

                // Status Badge
                Box(
                    modifier = Modifier
                        .background(
                            statusColor.copy(alpha = 0.2f),
                            RoundedCornerShape(12.dp)
                        )
                        .border(
                            1.dp,
                            statusColor.copy(alpha = 0.5f),
                            RoundedCornerShape(12.dp)
                        )
                        .padding(horizontal = 12.dp, vertical = 6.dp)
                ) {
                    Text(
                        incident.status,
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Bold,
                        color = statusColor
                    )
                }
            }

            // Location and Time
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        Icons.Default.LocationOn,
                        contentDescription = "Location",
                        tint = BlueAccent,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        incident.location,
                        fontSize = 14.sp,
                        color = BlueAccent,
                        fontWeight = FontWeight.Medium
                    )
                }

                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        Icons.Default.Schedule,
                        contentDescription = "Time",
                        tint = GrayText,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        incident.time,
                        fontSize = 14.sp,
                        color = GrayText
                    )
                }
            }

            // Employee Information
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier
                        .size(40.dp)
                        .background(PurpleAccent.copy(alpha = 0.3f), CircleShape),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        Icons.Default.Person,
                        contentDescription = "Employee",
                        tint = PurpleAccent,
                        modifier = Modifier.size(20.dp)
                    )
                }

                Spacer(modifier = Modifier.width(12.dp))

                Column {
                    Text(
                        incident.empName,
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Bold,
                        color = WhiteText
                    )
                    Text(
                        "ID: ${incident.empId}",
                        fontSize = 12.sp,
                        color = GrayText
                    )
                }
            }
        }
    }
}

@Composable
fun AdvancedEmployeeMonitoring(employees: List<EmployeeData>) {
    Column(
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        // Summary Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(20.dp),
            colors = CardDefaults.cardColors(containerColor = DarkCard),
            elevation = CardDefaults.cardElevation(defaultElevation = 6.dp)
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(Color(0xFF4CAF50).copy(alpha = 0.1f))
                    .padding(20.dp),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                val normalCount = employees.count { it.prediction == 0 }
                val flaggedCount = employees.count { it.prediction == 1 }

                QuickStat("Total", employees.size.toString(), WhiteText, Icons.Default.People)
                QuickStat("Normal", normalCount.toString(), GreenAccent, Icons.Default.CheckCircle)
                QuickStat("Flagged", flaggedCount.toString(), if (flaggedCount > 0) RedAlert else GreenAccent, Icons.Default.Warning)
            }
        }

        // Employee Cards
        employees.forEach { employee ->
            AdvancedEmployeeCard(employee = employee)
        }
    }
}

@Composable
fun QuickStat(label: String, value: String, color: Color, icon: ImageVector) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        Icon(
            imageVector = icon,
            contentDescription = label,
            tint = color,
            modifier = Modifier.size(24.dp)
        )
        Text(
            text = value,
            fontSize = 18.sp,
            fontWeight = FontWeight.Bold,
            color = color
        )
        Text(
            text = label,
            fontSize = 12.sp,
            color = GrayText
        )
    }
}

@Composable
fun AdvancedEmployeeCard(employee: EmployeeData) {
    val statusColor = if (employee.prediction == 1) RedAlert else GreenAccent
    val confidencePercent = (employee.confidenceScore * 100).toInt()
    val statusGradient = if (employee.prediction == 1) RedGradient else GreenGradient

    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(containerColor = DarkCard),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .background(Color(0xFF4CAF50).copy(alpha = 0.1f))
                .padding(20.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Profile Section
            Box(
                modifier = Modifier
                    .size(50.dp)
                    .background(statusColor.copy(alpha = 0.3f), CircleShape)
                    .border(2.dp, statusColor.copy(alpha = 0.5f), CircleShape),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = employee.name.split(" ").map { it.first() }.take(2).joinToString(""),
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Bold,
                    color = statusColor
                )
            }

            Spacer(modifier = Modifier.width(16.dp))

            // Employee Info
            Column(
                modifier = Modifier.weight(1f),
                verticalArrangement = Arrangement.spacedBy(6.dp)
            ) {
                Text(
                    employee.name,
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Bold,
                    color = WhiteText
                )

                Row(
                    horizontalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    Text(
                        "ID: ${employee.empId}",
                        fontSize = 13.sp,
                        color = BlueAccent
                    )
                    Text(
                        "📍 ${employee.location}",
                        fontSize = 13.sp,
                        color = GrayText
                    )
                }

                Row(
                    horizontalArrangement = Arrangement.spacedBy(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        "Confidence: $confidencePercent%",
                        fontSize = 12.sp,
                        color = GrayText
                    )

                    Text(
                        employee.timestamp.split(" ")[1],
                        fontSize = 12.sp,
                        color = GrayText
                    )
                }
            }

            // Status Badge
            Box(
                modifier = Modifier
                    .background(
                        statusColor.copy(alpha = 0.2f),
                        RoundedCornerShape(12.dp)
                    )
                    .border(
                        1.dp,
                        statusColor.copy(alpha = 0.5f),
                        RoundedCornerShape(12.dp)
                    )
                    .padding(horizontal = 12.dp, vertical = 8.dp)
            ) {
                Text(
                    employee.status,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Bold,
                    color = statusColor
                )
            }
        }
    }
}

@Composable
fun ModernSystemStatus(metrics: SimpleMetrics) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(24.dp),
        colors = CardDefaults.cardColors(containerColor = DarkCard),
        elevation = CardDefaults.cardElevation(defaultElevation = 8.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .background(
                    Brush.verticalGradient(
                        colors = listOf(
                            DarkCard,
                            DarkerCard
                        )
                    )
                )
                .padding(28.dp),
            verticalArrangement = Arrangement.spacedBy(20.dp)
        ) {
            // Header
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Icon(
                    Icons.Default.Settings,
                    contentDescription = "System Status",
                    tint = BlueAccent,
                    modifier = Modifier.size(28.dp)
                )
                Text(
                    "System Status Monitor",
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Bold,
                    color = WhiteText
                )
            }

            // Status Items
            StatusRow(
                "Security Level",
                metrics.securityLevel,
                when (metrics.securityLevel) {
                    "SECURE" -> GreenAccent
                    "MODERATE" -> YellowWarn
                    "HIGH ALERT" -> RedAlert
                    else -> BlueAccent
                },
                Icons.Default.Security
            )

            StatusRow(
                "Live Monitoring",
                metrics.lastScan,
                GreenAccent,
                Icons.Default.Visibility
            )

            StatusRow(
                "Systems Online",
                "${metrics.systemsOnline}%",
                if (metrics.systemsOnline > 90) GreenAccent else OrangeWarn,
                Icons.Default.Computer
            )

            StatusRow(
                "Active Threats",
                if (metrics.activeThreats > 0) "${metrics.activeThreats} Detected" else "None",
                if (metrics.activeThreats > 0) RedAlert else GreenAccent,
                Icons.Default.Warning
            )

            StatusRow(
                "Monitored Users",
                "${metrics.employeesMonitored} Active",
                BlueAccent,
                Icons.Default.People
            )

            // Performance Metrics
            Spacer(modifier = Modifier.height(8.dp))

            Text(
                "Performance Metrics",
                fontSize = 16.sp,
                fontWeight = FontWeight.Bold,
                color = LightGray
            )

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                MetricIndicator("CPU", "23%", GreenAccent)
                MetricIndicator("Memory", "67%", YellowWarn)
                MetricIndicator("Network", "12%", GreenAccent)
                MetricIndicator("Storage", "45%", GreenAccent)
            }
        }
    }
}

@Composable
fun StatusRow(label: String, value: String, color: Color, icon: ImageVector) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            Icon(
                imageVector = icon,
                contentDescription = label,
                tint = color,
                modifier = Modifier.size(20.dp)
            )
            Text(
                label,
                fontSize = 16.sp,
                color = GrayText,
                fontWeight = FontWeight.Medium
            )
        }

        Text(
            value,
            fontSize = 16.sp,
            fontWeight = FontWeight.Bold,
            color = color
        )
    }
}

@Composable
fun MetricIndicator(label: String, value: String, color: Color) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        Box(
            modifier = Modifier
                .size(50.dp)
                .background(
                    color.copy(alpha = 0.2f),
                    CircleShape
                )
                .border(2.dp, color.copy(alpha = 0.5f), CircleShape),
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = value,
                fontSize = 12.sp,
                fontWeight = FontWeight.Bold,
                color = color
            )
        }

        Text(
            label,
            fontSize = 12.sp,
            color = GrayText,
            fontWeight = FontWeight.Medium
        )
    }
}

@Composable
fun FloatingElements() {
    // Floating decorative elements
    val infiniteTransition = rememberInfiniteTransition(label = "floating")

    val float1 by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 10f,
        animationSpec = infiniteRepeatable(
            animation = tween(3000, easing = EaseInOutSine),
            repeatMode = RepeatMode.Reverse
        ), label = "float1"
    )

    val float2 by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = -8f,
        animationSpec = infiniteRepeatable(
            animation = tween(4000, easing = EaseInOutSine),
            repeatMode = RepeatMode.Reverse
        ), label = "float2"
    )

    // Floating accent elements (subtle)
    Box(
        modifier = Modifier
            .fillMaxSize()
            .offset(x = 50.dp, y = 100.dp + float1.dp)
    ) {
        Box(
            modifier = Modifier
                .size(4.dp)
                .background(
                    BlueAccent.copy(alpha = 0.3f),
                    CircleShape
                )
        )
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .offset(x = (-30).dp, y = 300.dp + float2.dp)
    ) {
        Box(
            modifier = Modifier
                .size(6.dp)
                .background(
                    GreenAccent.copy(alpha = 0.2f),
                    CircleShape
                )
        )
    }
}
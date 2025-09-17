package com.example.theftdetector


import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.platform.LocalContext
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.example.theftdetector.data.UserPreferences
import com.example.theftdetector.ui.LoginScreen

@Composable
fun AppNavigation(
    onGoogleSignIn: () -> Unit,
    onGitHubSignIn: () -> Unit,
    onLogout: () -> Unit
) {
    val context = LocalContext.current
    val prefs = UserPreferences(context)
    val navController: NavHostController = rememberNavController()

    val startDestination = if (prefs.isLoggedIn()) "home" else "login"



    NavHost(
        navController = navController,
        startDestination = startDestination
    ) {
        composable("login") {
            LoginScreen(
                onGoogleSignIn = {
                    onGoogleSignIn()
                },
                onGitHubSignIn = {
                    onGitHubSignIn()
                }
            )
        }

        composable("home") {
            HomeScreen(
                onLogout = {
                    onLogout()
                    navController.navigate("login") {
                        popUpTo("home") { inclusive = true }
                    }


                } ,
                onGoToDashboard = { navController.navigate("dashboard") }
            )
        }
        composable("dashboard") {
            DashboardScreen( onBack = {
                navController.popBackStack()
            })
        }


    }
}

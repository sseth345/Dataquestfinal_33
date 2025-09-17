plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.compose)
    id("com.google.gms.google-services") // 🔥 Add th
    id("org.jetbrains.kotlin.kapt")
}

android {
    namespace = "com.example.theftdetector"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.example.theftdetector"
        minSdk = 24
        targetSdk = 35
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"



    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
    kotlinOptions {
        jvmTarget = "11"
    }
    buildFeatures {
        compose = true
    }
}

dependencies {

    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.runtime.ktx)
    implementation(libs.androidx.activity.compose)
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.ui)
    implementation(libs.androidx.ui.graphics)
    implementation(libs.androidx.ui.tooling.preview)
    implementation(libs.androidx.material3)
    testImplementation(libs.junit)
    androidTestImplementation(libs.androidx.junit)
    androidTestImplementation(libs.androidx.espresso.core)
    androidTestImplementation(platform(libs.androidx.compose.bom))
    androidTestImplementation(libs.androidx.ui.test.junit4)
    debugImplementation(libs.androidx.ui.tooling)
    debugImplementation(libs.androidx.ui.test.manifest)

    implementation (platform("com.google.firebase:firebase-bom:32.7.0"))
    implementation ("com.google.firebase:firebase-auth-ktx")
    implementation ("com.google.firebase:firebase-firestore-ktx")

    // Google Sign-In
    implementation ("com.google.android.gms:play-services-auth:20.7.0")

    // GitHub OAuth (using custom implementation)
    implementation ("com.squareup.retrofit2:retrofit:2.9.0")
    implementation ("com.squareup.retrofit2:converter-gson:2.9.0")
    implementation ("com.squareup.okhttp3:logging-interceptor:4.12.0")

    // Icons
    implementation ("androidx.compose.material:material-icons-extended:1.5.4")
    // ViewModel
    implementation ("androidx.lifecycle:lifecycle-viewmodel-compose:2.7.0")

    // Animation
    implementation ("androidx.compose.animation:animation:1.5.4")

    implementation ("androidx.navigation:navigation-compose:2.7.7")

    implementation ("com.google.firebase:firebase-storage-ktx:20.3.0")

    implementation("androidx.credentials:credentials:1.3.0")
    implementation("androidx.credentials:credentials-play-services-auth:1.3.0")
    implementation("com.google.android.libraries.identity.googleid:googleid:1.1.1")
    // CameraX
    implementation ("androidx.camera:camera-camera2:1.3.1")
    implementation ("androidx.camera:camera-lifecycle:1.3.1")
    implementation ("androidx.camera:camera-view:1.3.1")



    // ML Kit Object Detection
    implementation ("com.google.mlkit:object-detection:17.0.0")

    implementation ("org.tensorflow:tensorflow-lite:2.13.0")
    implementation ("org.tensorflow:tensorflow-lite-task-vision:0.4.3")
    implementation ("org.tensorflow:tensorflow-lite-support:0.4.3")

    // Room
    val room_version = "2.6.1";
    implementation ("androidx.room:room-runtime:$room_version")
    kapt("androidx.room:room-compiler:2.6.1")

// Optional - Kotlin Extensions and Coroutines support
    implementation ("androidx.room:room-ktx:$room_version")

// Optional - Paging 3 support (if you're using paging with Room)
    implementation ("androidx.room:room-paging:$room_version")

    // Hilt Core
    implementation("com.google.dagger:hilt-android:2.51")
    kapt("com.google.dagger:hilt-android-compiler:2.51")

// Hilt for ViewModel
    implementation("androidx.hilt:hilt-navigation-compose:1.1.0")
    kapt("androidx.hilt:hilt-compiler:1.1.0")

}
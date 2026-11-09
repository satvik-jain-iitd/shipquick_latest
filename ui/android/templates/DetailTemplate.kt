// ShipQuick Android template: a detail screen (story #134). Only Compose Material 3 parts and the theme (rule 38).
// Spacing: 16dp = spacing.md, 24dp = spacing.lg.
package com.shipquick.ui.templates

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.BottomAppBar
import androidx.compose.material3.Button
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

/** One item, read top to bottom. The main action stays in a bottom bar while the text scrolls. */
@OptIn(ExperimentalMaterial3Api::class) // TopAppBar is experimental in the stable M3 releases
@Composable
fun DetailTemplate(
    title: String,
    headline: String,
    body: String,
    actionLabel: String,
    onBack: () -> Unit,
    onAction: () -> Unit,
) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(title) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
            )
        },
        bottomBar = {
            BottomAppBar {
                Button(onClick = onAction, modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp)) { Text(actionLabel) }
            }
        },
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            Text(headline, style = MaterialTheme.typography.headlineSmall)
            Text(body, style = MaterialTheme.typography.bodyLarge, modifier = Modifier.padding(bottom = 24.dp))
        }
    }
}

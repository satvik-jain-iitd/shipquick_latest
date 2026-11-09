// ShipQuick Android template: a step flow, like onboarding (story #134). Only Compose Material 3 parts and the theme (rule 38).
// docs/DESIGN_PROCESS.md section 12: the filled button is LAST, anchored at the bottom, in the same place on every step;
// the outline button sits above it; the hero sits in a box of fixed height, so its centre is the same on every step;
// on a typing step the buttons ride on top of the keyboard (imePadding). Spacing: 16dp = spacing.md, 24dp = spacing.lg.
package com.shipquick.ui.templates

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.text.input.TextFieldState
import androidx.compose.material3.Button
import androidx.compose.material3.Icon
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextField
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp

data class FlowStep(
    val title: String,
    val body: String,
    val hero: ImageVector,
    val heroDescription: String,
    val mainLabel: String,
    val altLabel: String? = null,
    val fieldLabel: String? = null,
)

/** Steps the user taps through with one thumb. onAlt gets the step index; onDone gets each typed answer by step index. */
@Composable
fun StepFlowTemplate(
    steps: List<FlowStep>,
    onAlt: (Int) -> Unit,
    onDone: (Map<Int, String>) -> Unit,
) {
    var index by remember { mutableIntStateOf(0) }
    val answers = remember { mutableMapOf<Int, String>() }
    val step = steps[index]
    val field = remember(index) { TextFieldState() } // a fresh field on each step
    Scaffold { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .imePadding()
                .padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            LinearProgressIndicator(progress = { (index + 1f) / steps.size }, modifier = Modifier.fillMaxWidth())
            Box(Modifier.fillMaxWidth().height(200.dp), contentAlignment = Alignment.Center) {
                Icon(step.hero, contentDescription = step.heroDescription, modifier = Modifier.size(96.dp))
            }
            Text(step.title, style = MaterialTheme.typography.headlineSmall, textAlign = TextAlign.Center, modifier = Modifier.fillMaxWidth())
            Text(step.body, style = MaterialTheme.typography.bodyLarge, textAlign = TextAlign.Center, modifier = Modifier.fillMaxWidth())
            step.fieldLabel?.let { label ->
                TextField(state = field, label = { Text(label) }, modifier = Modifier.fillMaxWidth())
            }
            Spacer(Modifier.weight(1f))
            step.altLabel?.let { alt ->
                OutlinedButton(onClick = { onAlt(index) }, modifier = Modifier.fillMaxWidth()) { Text(alt) }
            }
            Button(
                onClick = {
                    if (step.fieldLabel != null) answers[index] = field.text.toString()
                    if (index < steps.lastIndex) index++ else onDone(answers.toMap())
                },
                modifier = Modifier.fillMaxWidth().padding(bottom = 24.dp),
            ) { Text(step.mainLabel) }
        }
    }
}

// Fixture (story #185): a screen that breaks every Android UI lint rule at least once. detekt and Konsist must fail it.
// Both read text only; this file is never compiled.
package fixture.bad

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.gestures.draggable
import androidx.compose.foundation.gestures.transformable
import androidx.compose.foundation.shape.GenericShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.Button
import androidx.compose.ui.draw.*
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.draw.drawWithContent
import androidx.compose.ui.draw.drawWithCache
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Shape
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.foundation.clickable
import androidx.compose.ui.viewinterop.AndroidView
import androidx.compose.runtime.Composable
import android.widget.Button as ViewButton
import com.google.android.material.button.MaterialButton
import com.example.fancyui.FancyChip

val Brand = Color(0xFF112233)

fun Modifier.glow() = drawBehind { }

class Blob : Shape

object Pill : Shape

@Composable
fun BadScreen() {
    Canvas(modifier = Modifier) { }
    Box(Modifier.drawBehind { }.drawWithContent { drawContent() }.drawWithCache { })
    Text("Hi", color = Color(0xFF00FF00))
    Box(Modifier.background(Color.Red), shape = RoundedCornerShape(8.dp))
    Box(shape = GenericShape { _, _ -> })
    Text("Red", color = Color.Red)
    Box(Modifier.pointerInput(Unit) { detectTapGestures { } ; detectDragGestures { _, _ -> } })
    Box(Modifier.draggable(state, Orientation.Horizontal).transformable(state))
    AndroidView(factory = { ctx -> View(ctx) })
    Box(Modifier.clickable { }) { Text("Save") }
}

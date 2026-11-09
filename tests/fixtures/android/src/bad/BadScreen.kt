// Fixture (story #185): a screen that breaks every Android UI lint rule at least once. detekt and Konsist must fail it.
// Both read text only; this file is never compiled.
package fixture.bad

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.shape.GenericShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.Button
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.draw.drawWithContent
import androidx.compose.ui.draw.drawWithCache
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Shape
import androidx.compose.runtime.Composable
import android.widget.Button as ViewButton
import com.google.android.material.button.MaterialButton
import com.example.fancyui.FancyChip

class Blob : Shape

object Pill : Shape

@Composable
fun BadScreen() {
    Canvas(modifier = Modifier) { }
    Box(Modifier.drawBehind { }.drawWithContent { drawContent() }.drawWithCache { })
    Text("Hi", color = Color(0xFF00FF00))
    Box(Modifier.background(Color.Red), shape = RoundedCornerShape(8.dp))
    Box(shape = GenericShape { _, _ -> })
}

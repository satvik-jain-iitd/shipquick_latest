// Fixture (story #218): the one file where raw colours and fixed fonts are allowed. The token rules carry
// `excluded: '.*Tokens\.swift'`, so SwiftLint passes the Good folder with this file in it.
// SwiftLint reads text only; this file is never compiled.
import SwiftUI

enum Tokens {
    static let brand = Color(red: 0.1, green: 0.4, blue: 0.9)
    static let brandUI = UIColor(red: 0.1, green: 0.4, blue: 0.9, alpha: 1)
    static let caption = Font.system(size: 12)
    static let display = Font.custom("Inter", size: 34)
    static let space2: CGFloat = 8
    static let space3: CGFloat = 12
    static let icon48: CGFloat = 48
}

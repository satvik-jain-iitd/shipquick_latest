// Template: a step flow (onboarding, sign-up). Copy it, then change only the content (rule 38).
// DESIGN_PROCESS rule 12: the filled main button is last, at the bottom, in the same place on every step;
// the bordered alternative sits above it; the bar is a bottom safe-area inset, so it rides above the keyboard.
import SwiftUI

public struct StepFlowTemplate: View {
    struct Step {
        let symbol: String
        let title: String
        let text: String
        let asksName: Bool
    }

    private let steps = [
        Step(symbol: "hand.wave", title: "Welcome", text: "One line on what the app does.", asksName: false),
        Step(symbol: "person", title: "Your name", text: "We use it to greet you.", asksName: true),
        Step(symbol: "checkmark.circle", title: "All set", text: "One line on what happens next.", asksName: false),
    ]

    @State private var index = 0
    @State private var name = ""

    public init() {}

    public var body: some View {
        let step = steps[index]
        NavigationStack {
            VStack {
                ProgressView(value: Double(index + 1), total: Double(steps.count))
                // Two equal flexible halves: the hero's centre sits on the same line on every step (rule 12.3).
                Image(systemName: step.symbol)
                    .font(.largeTitle)
                    .imageScale(.large)
                    .accessibilityHidden(true)
                    .frame(maxHeight: .infinity)
                VStack {
                    Text(step.title).font(.title).bold()
                    Text(step.text).multilineTextAlignment(.center).foregroundStyle(.secondary)
                    if step.asksName {
                        TextField("Name", text: $name)
                            .textContentType(.name)
                            .textFieldStyle(.roundedBorder)
                    }
                }
                .frame(maxHeight: .infinity, alignment: .top)
            }
            .padding()
            .safeAreaInset(edge: .bottom) {
                VStack {
                    if index > 0 {
                        Button { index -= 1 } label: { Text("Back").frame(maxWidth: .infinity) }
                            .buttonStyle(.bordered)
                    }
                    Button { if index < steps.count - 1 { index += 1 } } label: {
                        Text(index < steps.count - 1 ? "Continue" : "Start").frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.borderedProminent)
                    .disabled(step.asksName && name.isEmpty)
                }
                .controlSize(.large)
                .padding()
            }
            .navigationBarTitleDisplayMode(.inline)
        }
    }
}

#Preview { StepFlowTemplate() }

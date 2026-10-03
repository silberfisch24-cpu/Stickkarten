import SwiftUI
import PDFKit
import StickCore
import StickPDF

struct PDFPreview: UIViewRepresentable {
    let data: Data

    func makeUIView(context: Context) -> PDFView {
        let v = PDFView()
        v.autoScales = true
        v.displayMode = .singlePageContinuous
        v.displayDirection = .vertical
        v.backgroundColor = .secondarySystemBackground
        return v
    }

    func updateUIView(_ v: PDFView, context: Context) {
        v.document = PDFDocument(data: data)
    }
}

enum ExportKind: String, CaseIterable, Identifiable {
    case lochmuster = "Lochmuster 1:1"
    case anleitung = "Anleitung"
    var id: String { rawValue }
}

/// PDF-Ausgabe: Lochmuster im Maßstab 1:1 (A4) und mehrseitige Anleitung — teilen oder per AirPrint drucken.
struct ExportView: View {
    @EnvironmentObject private var model: AppModel
    @Environment(\.dismiss) private var dismiss
    @State private var kind: ExportKind = .lochmuster
    @State private var lochmuster: Data?
    @State private var anleitung: Data?
    @State private var lochURL: URL?
    @State private var anleitungURL: URL?

    private var currentData: Data? { kind == .lochmuster ? lochmuster : anleitung }
    private var currentURL: URL? { kind == .lochmuster ? lochURL : anleitungURL }

    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                Picker("PDF", selection: $kind) {
                    ForEach(ExportKind.allCases) { Text($0.rawValue).tag($0) }
                }
                .pickerStyle(.segmented)
                .padding()

                if let data = currentData {
                    PDFPreview(data: data)
                } else {
                    Spacer()
                    ProgressView("PDF wird erzeugt …")
                    Spacer()
                }

                if kind == .lochmuster {
                    hinweis
                }
            }
            .navigationTitle("Drucken & Teilen")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) { Button("Schließen") { dismiss() } }
                ToolbarItemGroup(placement: .confirmationAction) {
                    if let url = currentURL {
                        ShareLink(item: url) { Label("Teilen", systemImage: "square.and.arrow.up") }
                    }
                    Button { printCurrent() } label: { Label("AirPrint", systemImage: "printer") }
                        .disabled(currentData == nil)
                }
            }
            .task { await generate() }
        }
    }

    private var hinweis: some View {
        let plan = Lochmuster.plan(model.result)
        return Group {
            if plan.fits {
                Text("Beim Drucken A4 und „Tatsächliche Größe“ (100 %) wählen, nicht „An Seite anpassen“. Mit dem 50-mm-Balken am Blattrand den Ausdruck nachmessen.")
            } else {
                Text("Dieser Zuschnitt ist größer als A4 und wird auf \(Int((plan.scale * 100).rounded())) % verkleinert — nicht zum direkten Anstechen geeignet.")
                    .foregroundStyle(Color(hex: gefahrFarbeHex))
            }
        }
        .font(.footnote)
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
    }

    private func generate() async {
        let result = model.result
        await Task.yield()
        let l = Lochmuster.pdf(result)
        lochmuster = l
        lochURL = write(l, name: "Stickkarten-Lochmuster.pdf")
        await Task.yield()
        let a = Anleitung.pdf(result)
        anleitung = a
        anleitungURL = write(a, name: "Stickkarten-Anleitung.pdf")
    }

    private func write(_ data: Data, name: String) -> URL? {
        let url = FileManager.default.temporaryDirectory.appendingPathComponent(name)
        do {
            try data.write(to: url, options: .atomic)
            return url
        } catch {
            return nil
        }
    }

    private func printCurrent() {
        guard let data = currentData else { return }
        let info = UIPrintInfo(dictionary: nil)
        info.outputType = .general
        info.jobName = kind == .lochmuster ? "Stickkarten-Lochmuster" : "Stickkarten-Anleitung"
        let controller = UIPrintInteractionController.shared
        controller.printInfo = info
        controller.printingItem = data
        controller.showsPaperSelectionForLoadedPapers = true
        controller.present(animated: true, completionHandler: nil)
    }
}

// Paste into Power Query Advanced Editor and name the query VerifiedKPI.
let
    Source = Csv.Document(Web.Contents("https://raw.githubusercontent.com/Krgaurav93084/Brazil-Stock-Market-StarSchema/main/analytics_v2/verified_kpis.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Types = Table.TransformColumnTypes(Headers, {{"metric", type text}, {"value", type number}, {"unit", type text}}, "en-US")
in
    Types

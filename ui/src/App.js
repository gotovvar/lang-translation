import React, { useState } from "react";
import axios from "axios";

function App() {
  const [inputText, setInputText] = useState("");
  const [results, setResults] = useState(null);
  const [syntaxTree, setSyntaxTree] = useState(null);
  const [selectedSentence, setSelectedSentence] = useState("");
  const [sentences, setSentences] = useState([]);
  const [loading, setLoading] = useState(false);
  const [treeLoading, setTreeLoading] = useState(false);

  const splitIntoSentences = (text) => {
    return text.match(/[^.!?]+[.!?]*/g) || [];
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResults(null);
    setSyntaxTree(null);

    try {
      const response = await axios.post("http://localhost:8000/api/v0/translation", {
        text: inputText,
      });

      setResults(response.data);

      const splitSentences = splitIntoSentences(inputText);
      setSentences(splitSentences);
    } catch (error) {
      console.error("Error during API call:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateTree = async () => {
    if (!selectedSentence) return;

    setTreeLoading(true);
    setSyntaxTree(null);

    try {
      const response = await axios.post(
        "http://localhost:8000/api/v0/tree",
        { text: selectedSentence },
        { responseType: "arraybuffer" } // To handle binary response
      );

      const blob = new Blob([response.data], { type: "image/png" });
      const url = URL.createObjectURL(blob);

      setSyntaxTree(url);
    } catch (error) {
      console.error("Error during tree generation API call:", error);
    } finally {
      setTreeLoading(false);
    }
  };

  const handleDownloadResults = () => {
    if (!results) return;

    let fileContent = "Translation Results\n\n";

    fileContent += "\nOriginal Text:\n";
    fileContent += `${results.original_text}\n\n`;

    fileContent += "Original Text Analysis:\n";
    fileContent += `Words Count: ${results.original_text_analysis.words_count}\n`;
    fileContent += "Words Info:\n";
    results.original_text_analysis.words_info.forEach((info) => {
      fileContent += `  - Word: ${info.word}, Frequency: ${info.freq}, Grammatical Info: ${info.gram_info}\n`;
    });

    fileContent += "\nTranslated Text:\n";
    fileContent += `${results.translated_text}\n\n`;

    fileContent += "Translated Text Analysis:\n";
    fileContent += `Words Count: ${results.translated_text_analysis.words_count}\n`;
    fileContent += "Words Info:\n";
    results.translated_text_analysis.words_info.forEach((info) => {
      fileContent += `  - Word: ${info.word}, Frequency: ${info.freq}, Grammatical Info: ${info.gram_info}\n`;
    });

    const blob = new Blob([fileContent], { type: "text/plain;charset=utf-8" });

    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "translation_results.txt";

    document.body.appendChild(link);
    link.click();

    document.body.removeChild(link);
  };

  const renderWordsTable = (wordsInfo) => {
    return (
      <table
        style={{
          borderCollapse: "collapse",
          width: "100%",
          marginTop: "10px",
          textAlign: "left",
          fontSize: "14px",
        }}
      >
        <thead>
          <tr style={{ borderBottom: "2px solid #ccc" }}>
            <th style={{ padding: "10px" }}>Word</th>
            <th style={{ padding: "10px" }}>Frequency</th>
            <th style={{ padding: "10px" }}>Grammatical Info</th>
          </tr>
        </thead>
        <tbody>
          {wordsInfo.map((info, index) => (
            <tr key={index} style={{ borderBottom: "1px solid #eee" }}>
              <td style={{ padding: "10px" }}>{info.word}</td>
              <td style={{ padding: "10px" }}>{info.freq}</td>
              <td style={{ padding: "10px" }}>{info.gram_info}</td>
            </tr>
          ))}
        </tbody>
      </table>
    );
  };

  return (
    <div style={{ padding: "20px", fontFamily: "Arial, sans-serif" }}>
      <h1>Text Processing App</h1>
      <form onSubmit={handleSubmit} style={{ marginBottom: "20px" }}>
        <textarea
          placeholder="Enter your text here..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          rows={5}
          cols={50}
          style={{ marginBottom: "10px", width: "100%", padding: "10px" }}
        />
        <br />
        <button type="submit" style={{ padding: "10px 20px", cursor: "pointer" }}>
          Process Text
        </button>
      </form>

      {loading && <p>Processing...</p>}

      {results && (
        <div>
          <h2>Results</h2>
          <p><strong>Original Text Analysis:</strong></p>
          <p>Words Count: {results.original_text_analysis.words_count}</p>
          {renderWordsTable(results.original_text_analysis.words_info)}
          <p><strong>Translated Text:</strong> {results.translated_text}</p>
          <p><strong>Translated Text Analysis:</strong></p>
          <p>Words Count: {results.translated_text_analysis.words_count}</p>
          {renderWordsTable(results.translated_text_analysis.words_info)}

          {sentences.length > 0 && (
            <div style={{ marginTop: "20px" }}>
              <h3>Sentences</h3>
              <ul>
                {sentences.map((sentence, index) => (
                  <li key={index} style={{ marginBottom: "5px" }}>
                    <label>
                      <input
                        type="radio"
                        name="sentence"
                        value={sentence}
                        onChange={() => setSelectedSentence(sentence)}
                        style={{ marginRight: "10px" }}
                      />
                      {sentence}
                    </label>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <button
            onClick={handleDownloadResults}
            style={{
              padding: "10px 20px",
              cursor: "pointer",
              marginTop: "20px",
              backgroundColor: "#28a745",
              color: "white",
              border: "none",
              borderRadius: "5px",
            }}
          >
            Download Results
          </button>
        </div>
      )}

      <button
        onClick={handleGenerateTree}
        style={{
          padding: "10px 20px",
          cursor: "pointer",
          marginTop: "20px",
          backgroundColor: selectedSentence ? "#007BFF" : "#ccc",
          color: "white",
          border: "none",
          borderRadius: "5px",
        }}
        disabled={!selectedSentence || treeLoading}
      >
        {treeLoading ? "Generating Tree..." : "Generate Syntax Tree"}
      </button>

      {syntaxTree && (
        <div style={{ marginTop: "20px" }}>
          <h2>Syntax Tree</h2>
          <img
            src={syntaxTree}
            alt="Syntax Tree"
            style={{ maxWidth: "100%", border: "1px solid #ccc", padding: "10px" }}
          />
        </div>
      )}
    </div>
  );
}

export default App;

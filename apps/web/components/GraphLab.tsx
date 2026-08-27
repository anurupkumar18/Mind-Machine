const nodes = [
  { id: "A", x: 50, y: 28 }, { id: "B", x: 22, y: 55 }, { id: "C", x: 78, y: 55 }, { id: "D", x: 50, y: 84 }
];
const edges = [["A", "B"], ["A", "C"], ["B", "D"], ["C", "D"], ["D", "A"]];

export function GraphLab({ predicted, onToggle, revealed, correct }: { predicted: string[]; onToggle: (node: string) => void; revealed: boolean; correct?: boolean }) {
  const byId = Object.fromEntries(nodes.map((node) => [node.id, node]));
  return <section className="panel graph-panel">
    <div className="panel-heading"><span className="step">02</span><div><h2>Externalize the next BFS state</h2><p>Start at A. Select the frontier after expanding A, then commit before seeing ground truth.</p></div></div>
    <div className="graph-workspace">
      <svg viewBox="0 0 100 100" role="img" aria-label="Directed graph with nodes A, B, C, and D">
        <defs><marker id="arrow" markerWidth="5" markerHeight="5" refX="4" refY="2.5" orient="auto"><path d="M0,0 L5,2.5 L0,5 Z" /></marker></defs>
        {edges.map(([from, to]) => <line key={`${from}-${to}`} x1={byId[from].x} y1={byId[from].y} x2={byId[to].x} y2={byId[to].y} markerEnd="url(#arrow)" />)}
        {nodes.map((node) => <g key={node.id}><circle cx={node.x} cy={node.y} r="9" className={predicted.includes(node.id) ? "active-node" : ""} /><text x={node.x} y={node.y + 1} textAnchor="middle">{node.id}</text></g>)}
      </svg>
      <div className="frontier-picker"><span className="eyebrow">Your predicted frontier</span><div>{nodes.filter((node) => node.id !== "A").map((node) => <button disabled={revealed} key={node.id} className={predicted.includes(node.id) ? "selected" : ""} onClick={() => onToggle(node.id)}>{node.id}</button>)}</div>{revealed && <p className={correct ? "success" : "failure"}>{correct ? "Correct: [B, C] is the canonical frontier." : "Ground truth: the canonical frontier is [B, C]."}</p>}</div>
    </div>
  </section>;
}


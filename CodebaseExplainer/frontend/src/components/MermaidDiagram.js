import React from 'react';
import mermaid from 'mermaid';

// Configure mermaid
mermaid.initialize({
  startOnLoad: false,
  theme: 'default',
  flowchart: {
    useMaxWidth: false,
    htmlLabels: true,
    curve: 'basis'
  },
  sequence: {
    useMaxWidth: false
  }
});

class MermaidDiagram extends React.Component {
  constructor(props) {
    super(props);
    this.containerRef = React.createRef();
  }

  componentDidMount() {
    this.renderDiagram();
  }

  componentDidUpdate() {
    this.renderDiagram();
  }

  renderDiagram = () => {
    if (this.containerRef.current) {
      mermaid.render(
        `diagram-${this.props.id || Date.now()}`,
        this.props.diagram,
        (svgCode) => {
          if (this.containerRef.current) {
            this.containerRef.current.innerHTML = svgCode;
          }
        }
      );
    }
  };

  render() {
    return (
      <div
        ref={this.containerRef}
        style={{
          width: '100%',
          minHeight: '200px',
          background: '#f5f5f5',
          borderRadius: '8px',
          padding: '20px'
        }}
      />
    );
  }
}

export default MermaidDiagram;

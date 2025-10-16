"""
Database layer using DuckDB for persistent storage
"""
import duckdb
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import numpy as np

from config import config
from core.models import SaaSIdea, Evaluation, IterationResult


class IdeaDatabase:
    """DuckDB-based storage for ideas, evaluations, and embeddings"""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or config.DATABASE_PATH
        self.conn = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Create database and tables if they don't exist"""
        config.ensure_directories()
        self.conn = duckdb.connect(str(self.db_path))
        
        # Ideas table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS ideas (
                idea_id VARCHAR PRIMARY KEY,
                idea_name VARCHAR NOT NULL,
                problem_statement TEXT NOT NULL,
                target_user VARCHAR NOT NULL,
                core_features JSON NOT NULL,
                differentiator TEXT NOT NULL,
                tech_stack JSON NOT NULL,
                revenue_model VARCHAR NOT NULL,
                domain VARCHAR NOT NULL,
                created_at TIMESTAMP NOT NULL,
                iteration INTEGER NOT NULL,
                parent_ideas JSON,
                embedding_id VARCHAR
            )
        """)
        
        # Evaluations table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS evaluations (
                evaluation_id VARCHAR PRIMARY KEY,
                idea_id VARCHAR NOT NULL,
                novelty DOUBLE NOT NULL,
                feasibility DOUBLE NOT NULL,
                market_fit DOUBLE NOT NULL,
                viability DOUBLE NOT NULL,
                composite_score DOUBLE,
                justification TEXT NOT NULL,
                evaluated_at TIMESTAMP NOT NULL,
                evaluated_by VARCHAR NOT NULL,
                FOREIGN KEY (idea_id) REFERENCES ideas(idea_id)
            )
        """)
        
        # Embeddings table (for semantic search)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (
                embedding_id VARCHAR PRIMARY KEY,
                idea_id VARCHAR NOT NULL,
                embedding DOUBLE[],
                created_at TIMESTAMP NOT NULL,
                FOREIGN KEY (idea_id) REFERENCES ideas(idea_id)
            )
        """)
        
        # Iterations table (for tracking creative loop progress)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS iterations (
                iteration_number INTEGER PRIMARY KEY,
                generated_count INTEGER NOT NULL,
                top_ideas JSON NOT NULL,
                best_score DOUBLE NOT NULL,
                strategist_notes TEXT,
                should_continue BOOLEAN NOT NULL,
                created_at TIMESTAMP NOT NULL
            )
        """)
        
        # System state table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS system_state (
                id INTEGER PRIMARY KEY,
                current_iteration INTEGER NOT NULL,
                total_ideas_generated INTEGER NOT NULL,
                best_score DOUBLE NOT NULL,
                converged BOOLEAN NOT NULL,
                domain_focus VARCHAR,
                started_at TIMESTAMP NOT NULL,
                last_updated TIMESTAMP NOT NULL
            )
        """)
        
        self.conn.commit()
    
    def insert_idea(self, idea: SaaSIdea) -> str:
        """Insert a new idea into the database"""
        import uuid
        
        if not idea.idea_id:
            idea.idea_id = str(uuid.uuid4())
        
        self.conn.execute("""
            INSERT INTO ideas VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            idea.idea_id,
            idea.idea_name,
            idea.problem_statement,
            idea.target_user,
            json.dumps(idea.core_features),
            idea.differentiator,
            json.dumps(idea.tech_stack),
            idea.revenue_model.value,
            idea.domain.value,
            idea.created_at,
            idea.iteration,
            json.dumps(idea.parent_ideas),
            None  # embedding_id to be added later
        ])
        
        self.conn.commit()
        return idea.idea_id
    
    def insert_evaluation(self, evaluation: Evaluation) -> str:
        """Insert an evaluation into the database"""
        import uuid
        
        eval_id = str(uuid.uuid4())
        
        self.conn.execute("""
            INSERT INTO evaluations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            eval_id,
            evaluation.idea_id,
            evaluation.novelty,
            evaluation.feasibility,
            evaluation.market_fit,
            evaluation.viability,
            evaluation.composite_score,
            evaluation.justification,
            evaluation.evaluated_at,
            evaluation.evaluated_by
        ])
        
        self.conn.commit()
        return eval_id
    
    def get_idea(self, idea_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve an idea by ID"""
        result = self.conn.execute("""
            SELECT * FROM ideas WHERE idea_id = ?
        """, [idea_id]).fetchone()
        
        if not result:
            return None
        
        columns = [desc[0] for desc in self.conn.description]
        return dict(zip(columns, result))
    
    def get_all_ideas(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve all ideas"""
        query = "SELECT * FROM ideas ORDER BY created_at DESC"
        if limit:
            query += f" LIMIT {limit}"
        
        results = self.conn.execute(query).fetchall()
        columns = [desc[0] for desc in self.conn.description]
        return [dict(zip(columns, row)) for row in results]
    
    def get_top_ideas(self, k: int = 5) -> List[Dict[str, Any]]:
        """Get top K ideas by composite score"""
        results = self.conn.execute("""
            SELECT i.*, e.composite_score
            FROM ideas i
            JOIN evaluations e ON i.idea_id = e.idea_id
            ORDER BY e.composite_score DESC
            LIMIT ?
        """, [k]).fetchall()
        
        columns = [desc[0] for desc in self.conn.description]
        return [dict(zip(columns, row)) for row in results]
    
    def get_ideas_by_iteration(self, iteration: int) -> List[Dict[str, Any]]:
        """Get all ideas from a specific iteration"""
        results = self.conn.execute("""
            SELECT * FROM ideas WHERE iteration = ?
        """, [iteration]).fetchall()
        
        columns = [desc[0] for desc in self.conn.description]
        return [dict(zip(columns, row)) for row in results]
    
    def insert_embedding(self, idea_id: str, embedding: np.ndarray) -> str:
        """Store embedding vector for an idea"""
        import uuid
        
        embedding_id = str(uuid.uuid4())
        
        self.conn.execute("""
            INSERT INTO embeddings VALUES (?, ?, ?, ?)
        """, [
            embedding_id,
            idea_id,
            embedding.tolist(),
            datetime.utcnow()
        ])
        
        # Update idea with embedding_id
        self.conn.execute("""
            UPDATE ideas SET embedding_id = ? WHERE idea_id = ?
        """, [embedding_id, idea_id])
        
        self.conn.commit()
        return embedding_id
    
    def get_all_embeddings(self) -> List[tuple]:
        """Get all embeddings (idea_id, embedding vector)"""
        results = self.conn.execute("""
            SELECT idea_id, embedding FROM embeddings
        """).fetchall()
        return [(row[0], np.array(row[1])) for row in results]
    
    def insert_iteration_result(self, result: IterationResult):
        """Store iteration results"""
        self.conn.execute("""
            INSERT INTO iterations VALUES (?, ?, ?, ?, ?, ?)
        """, [
            result.iteration_number,
            len(result.generated_ideas),
            json.dumps(result.top_ideas),
            max([e.composite_score for e in result.evaluations]) if result.evaluations else 0.0,
            result.strategist_notes,
            result.should_continue,
            datetime.utcnow()
        ])
        
        self.conn.commit()
    
    def update_system_state(self, state: Dict[str, Any]):
        """Update or insert system state"""
        # Check if state exists
        exists = self.conn.execute("SELECT COUNT(*) FROM system_state WHERE id = 1").fetchone()[0]
        
        if exists:
            self.conn.execute("""
                UPDATE system_state 
                SET current_iteration = ?,
                    total_ideas_generated = ?,
                    best_score = ?,
                    converged = ?,
                    domain_focus = ?,
                    last_updated = ?
                WHERE id = 1
            """, [
                state['current_iteration'],
                state['total_ideas_generated'],
                state['best_score'],
                state['converged'],
                state.get('domain_focus'),
                datetime.utcnow()
            ])
        else:
            self.conn.execute("""
                INSERT INTO system_state VALUES (1, ?, ?, ?, ?, ?, ?, ?)
            """, [
                state['current_iteration'],
                state['total_ideas_generated'],
                state['best_score'],
                state['converged'],
                state.get('domain_focus'),
                datetime.utcnow(),
                datetime.utcnow()
            ])
        
        self.conn.commit()
    
    def get_system_state(self) -> Optional[Dict[str, Any]]:
        """Get current system state"""
        result = self.conn.execute("""
            SELECT * FROM system_state WHERE id = 1
        """).fetchone()
        
        if not result:
            return None
        
        columns = [desc[0] for desc in self.conn.description]
        return dict(zip(columns, result))
    
    def export_top_ideas_to_json(self, output_path: Path, k: int = 10):
        """Export top K ideas to JSON file"""
        top_ideas = self.get_top_ideas(k)
        
        with open(output_path, 'w') as f:
            json.dump(top_ideas, f, indent=2, default=str)
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


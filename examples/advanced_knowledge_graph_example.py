import asyncio
from graphfusionai.knowledge_graph import KnowledgeGraph, Node, Edge
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    try:
        # Initialize knowledge graph
        logger.info("Initializing knowledge graph...")
        kg = KnowledgeGraph()

        # Example text for knowledge extraction
        text = """
        SpaceX, founded by Elon Musk, launched the Falcon 9 rocket from Kennedy Space Center.
        The rocket carried a payload of satellites into orbit. NASA collaborated with SpaceX
        on this mission to deliver supplies to the International Space Station. This mission
        demonstrates the strong partnership between SpaceX and NASA in space exploration.
        """

        logger.info("\nExtracting knowledge from text...")
        extracted_elements = kg.extract_knowledge_from_text(text)

        # Add extracted elements to graph
        for node, edge in extracted_elements:
            if node:
                logger.info(f"Adding node: {node.type} - {node.properties.get('text', 'Unknown')}")
                kg.add_node(node)
            if edge:
                logger.info(f"Adding edge: {edge.type} from {edge.source} to {edge.target}")
                kg.add_edge(edge)

        logger.info("\nPerforming reasoning...")
        # Example reasoning query
        query = "What is the relationship between SpaceX and NASA?"
        reasoning_results = kg.reason(query)

        logger.info(f"Query: {query}")
        for result in reasoning_results:
            logger.info(f"Found relationship for {result['query_entity']}:")
            for target_node, paths in result.get('related_paths', {}).items():
                logger.info(f"- Connection to {target_node}:")
                for path in paths:
                    logger.info(f"  Path: {' -> '.join(path)}")

        logger.info("\nInferring new relationships...")
        inferred_edges = kg.infer_relationships()

        logger.info(f"Found {len(inferred_edges)} inferred relationships:")
        for edge in inferred_edges:
            logger.info(f"Inferred {edge.type} relationship: {edge.source} -> {edge.target}")
            kg.add_edge(edge)

        # Save the knowledge graph
        kg.save("example_knowledge_graph.json")
        logger.info("\nKnowledge graph saved to example_knowledge_graph.json")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())
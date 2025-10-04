#!/usr/bin/env python3
"""
Simple Kafka setup script for local development
This script helps set up a local Kafka instance for the YouTube view simulation
"""

import subprocess
import sys
import os
import time
import requests
from pathlib import Path

def check_java():
    """Check if Java is installed"""
    try:
        result = subprocess.run(['java', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Java is installed")
            return True
        else:
            print("❌ Java is not installed")
            return False
    except FileNotFoundError:
        print("❌ Java is not installed")
        return False

def download_kafka():
    """Download and extract Kafka"""
    kafka_dir = Path("kafka")
    if kafka_dir.exists():
        print("✅ Kafka directory already exists")
        return str(kafka_dir)
    
    print("📥 Downloading Kafka...")
    try:
        # For Windows, we'll use a simple approach
        print("Please download Kafka from https://kafka.apache.org/downloads")
        print("Extract it to a 'kafka' folder in this directory")
        print("Or run: curl -s https://downloads.apache.org/kafka/2.13-3.6.0/kafka_2.13-3.6.0.tgz | tar -xz")
        return None
    except Exception as e:
        print(f"❌ Error downloading Kafka: {e}")
        return None

def start_zookeeper(kafka_dir):
    """Start Zookeeper"""
    print("🔄 Starting Zookeeper...")
    try:
        if os.name == 'nt':  # Windows
            zookeeper_cmd = [str(kafka_dir / "bin" / "windows" / "zookeeper-server-start.bat"), 
                           str(kafka_dir / "config" / "zookeeper.properties")]
        else:  # Unix-like
            zookeeper_cmd = [str(kafka_dir / "bin" / "zookeeper-server-start.sh"), 
                           str(kafka_dir / "config" / "zookeeper.properties")]
        
        # Start in background
        process = subprocess.Popen(zookeeper_cmd, 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        time.sleep(5)  # Wait for Zookeeper to start
        print("✅ Zookeeper started")
        return process
    except Exception as e:
        print(f"❌ Error starting Zookeeper: {e}")
        return None

def start_kafka(kafka_dir):
    """Start Kafka server"""
    print("🔄 Starting Kafka server...")
    try:
        if os.name == 'nt':  # Windows
            kafka_cmd = [str(kafka_dir / "bin" / "windows" / "kafka-server-start.bat"), 
                        str(kafka_dir / "config" / "server.properties")]
        else:  # Unix-like
            kafka_cmd = [str(kafka_dir / "bin" / "kafka-server-start.sh"), 
                        str(kafka_dir / "config" / "server.properties")]
        
        # Start in background
        process = subprocess.Popen(kafka_cmd, 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        time.sleep(10)  # Wait for Kafka to start
        print("✅ Kafka server started")
        return process
    except Exception as e:
        print(f"❌ Error starting Kafka: {e}")
        return None

def create_topic(kafka_dir):
    """Create the view-events topic"""
    print("🔄 Creating 'view-events' topic...")
    try:
        if os.name == 'nt':  # Windows
            topic_cmd = [str(kafka_dir / "bin" / "windows" / "kafka-topics.bat"), 
                        "--create", "--topic", "view-events", 
                        "--bootstrap-server", "localhost:9092", 
                        "--partitions", "1", "--replication-factor", "1"]
        else:  # Unix-like
            topic_cmd = [str(kafka_dir / "bin" / "kafka-topics.sh"), 
                        "--create", "--topic", "view-events", 
                        "--bootstrap-server", "localhost:9092", 
                        "--partitions", "1", "--replication-factor", "1"]
        
        result = subprocess.run(topic_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Topic 'view-events' created")
        else:
            print(f"⚠️ Topic might already exist: {result.stderr}")
        return True
    except Exception as e:
        print(f"❌ Error creating topic: {e}")
        return False

def main():
    print("🚀 Setting up Kafka for YouTube View Simulation")
    print("=" * 50)
    
    # Check Java
    if not check_java():
        print("\nPlease install Java 8 or higher first:")
        print("https://www.oracle.com/java/technologies/downloads/")
        return False
    
    # Check/Download Kafka
    kafka_dir = download_kafka()
    if not kafka_dir or not Path(kafka_dir).exists():
        print("\nPlease download and extract Kafka manually:")
        print("1. Go to https://kafka.apache.org/downloads")
        print("2. Download the latest binary")
        print("3. Extract to 'kafka' folder in this directory")
        return False
    
    kafka_path = Path(kafka_dir)
    if not (kafka_path / "bin").exists():
        print("❌ Kafka bin directory not found")
        return False
    
    print(f"✅ Using Kafka from: {kafka_path}")
    
    # Start services
    zookeeper_process = start_zookeeper(kafka_path)
    if not zookeeper_process:
        return False
    
    kafka_process = start_kafka(kafka_path)
    if not kafka_process:
        return False
    
    # Create topic
    create_topic(kafka_path)
    
    print("\n🎉 Kafka setup complete!")
    print("Kafka is running on localhost:9092")
    print("Topic 'view-events' is ready")
    print("\nPress Ctrl+C to stop Kafka")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping Kafka...")
        if kafka_process:
            kafka_process.terminate()
        if zookeeper_process:
            zookeeper_process.terminate()
        print("✅ Kafka stopped")

if __name__ == "__main__":
    main()


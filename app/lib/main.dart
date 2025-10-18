import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:bridge/bridge.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter + Rust Hybrid',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const MyHomePage(title: 'Flutter + Rust Hybrid'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key, required this.title});

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  String _version = 'Loading version...';
  String _crateName = '';

  @override
  void initState() {
    super.initState();
    _refreshVersion();
  }

  void _refreshVersion() {
    try {
      final rawVersion = coreVersion();
      final versionData = jsonDecode(rawVersion);
      
      setState(() {
        _crateName = versionData['crate_name'] ?? 'unknown';
        _version = versionData['crate_version'] ?? 'unknown';
      });
    } catch (e) {
      setState(() {
        _crateName = 'Error';
        _version = 'Error loading version: $e';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text(widget.title),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            const Text(
              'Core Version Metadata',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 24),
            Card(
              margin: const EdgeInsets.symmetric(horizontal: 24.0),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          'Crate Name:',
                          style: TextStyle(fontWeight: FontWeight.w600),
                        ),
                        Text(_crateName),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          'Version:',
                          style: TextStyle(fontWeight: FontWeight.w600),
                        ),
                        Text(_version),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),
            Text(
              'Platforms: Windows (MSVC), Android (arm64-v8a)',
              style: Theme.of(context).textTheme.bodySmall,
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _refreshVersion,
        tooltip: 'Refresh version',
        child: const Icon(Icons.refresh),
      ),
    );
  }
}

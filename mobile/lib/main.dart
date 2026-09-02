import 'package:flutter/material.dart';
import 'screens/home_selector.dart';

void main() {
  runApp(const TriageSystemApp());
}

class TriageSystemApp extends StatelessWidget {
  const TriageSystemApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Healthcare Triage System',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: const HomeSelectorScreen(),
    );
  }
}

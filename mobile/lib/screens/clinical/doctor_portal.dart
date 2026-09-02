import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../../config.dart';

class DoctorPortalScreen extends StatefulWidget {
  const DoctorPortalScreen({super.key});

  @override
  State<DoctorPortalScreen> createState() => _DoctorPortalScreenState();
}

class _DoctorPortalScreenState extends State<DoctorPortalScreen> {
  List<dynamic> patients = [];
  bool isLoading = true;
  String? error;

  @override
  void initState() {
    super.initState();
    _fetchPatients();
  }

  Future<void> _fetchPatients() async {
    try {
      final res = await http.get(Uri.parse('${AppConfig.apiBaseUrl}/api/dashboard/data'));
      if (res.statusCode == 200) {
        final data = jsonDecode(res.body);
        setState(() {
          patients = data['data']['mockPatients'] ?? [];
          isLoading = false;
        });
      } else {
        setState(() {
          error = 'Failed to load patients';
          isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        error = 'Connection Error: $e';
        isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF7F9FC),
      appBar: AppBar(
        title: const Text('Doctor Portal - Worklist', style: TextStyle(color: Color(0xFF191C1E), fontWeight: FontWeight.bold)),
        backgroundColor: Colors.white,
        elevation: 0,
        iconTheme: const IconThemeData(color: Color(0xFF191C1E)),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              setState(() {
                isLoading = true;
                error = null;
              });
              _fetchPatients();
            },
          )
        ],
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFF006B4D)))
          : error != null
              ? Center(child: Text(error!, style: const TextStyle(color: Color(0xFFB91C1C))))
              : ListView(
                  padding: const EdgeInsets.all(16.0),
                  children: [
                    const Text('Priority Scheduler - Clinical Queue', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF191C1E))),
                    const SizedBox(height: 16),
                    if (patients.isEmpty)
                      const Text('No patients in the queue.', style: TextStyle(color: Color(0xFF6B7280)))
                    else
                      ...patients.map((p) => _buildPatientCard(
                            p['name'] ?? 'Unknown',
                            p['department'] ?? 'Unknown',
                            p['triageLevel'] ?? 'Green',
                            p['waitTime'] ?? '0m',
                          )),
                  ],
                ),
    );
  }

  Color _getBadgeColor(String level) {
    switch (level.toLowerCase()) {
      case 'red':
        return const Color(0xFFBE123C);
      case 'yellow':
        return const Color(0xFFD97706);
      case 'green':
        return const Color(0xFF059669);
      default:
        return const Color(0xFF6B7280);
    }
  }
  
  Color _getBadgeBgColor(String level) {
    switch (level.toLowerCase()) {
      case 'red':
        return const Color(0xFFFFE4E6);
      case 'yellow':
        return const Color(0xFFFEF3C7);
      case 'green':
        return const Color(0xFFD1FAE5);
      default:
        return const Color(0xFFF3F4F6);
    }
  }

  Widget _buildPatientCard(String name, String complaint, String level, String waitTime) {
    final badgeColor = _getBadgeColor(level);
    final badgeBg = _getBadgeBgColor(level);
    
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFE5E7EB)),
        boxShadow: [
          BoxShadow(color: Colors.black.withOpacity(0.02), blurRadius: 4, offset: const Offset(0, 2)),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(child: Text(name, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: Color(0xFF191C1E)))),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(color: const Color(0xFFF3F4F6), borderRadius: BorderRadius.circular(12)),
                  child: Row(
                    children: [
                      const Icon(Icons.timer_outlined, size: 14, color: Color(0xFF6B7280)),
                      const SizedBox(width: 4),
                      Text(waitTime, style: const TextStyle(color: Color(0xFF4A4A4A), fontWeight: FontWeight.bold, fontSize: 12)),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text('Department: $complaint', style: const TextStyle(color: Color(0xFF6B7280), fontSize: 14)),
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(color: badgeBg, borderRadius: BorderRadius.circular(16)),
                  child: Row(
                    children: [
                      Icon(Icons.flag, size: 14, color: badgeColor),
                      const SizedBox(width: 4),
                      Text('Triage: ${level.toUpperCase()}', style: TextStyle(color: badgeColor, fontWeight: FontWeight.bold, fontSize: 12)),
                    ],
                  ),
                ),
                Row(
                  children: [
                    TextButton(
                      onPressed: () {
                        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Reviewing ABCDE for $name')));
                      },
                      child: const Text('Review ABCDE', style: TextStyle(color: Color(0xFF006B4D), fontWeight: FontWeight.w600)),
                    ),
                    const SizedBox(width: 8),
                    ElevatedButton(
                      onPressed: () {
                        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Took case: $name')));
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF006B4D),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                      ),
                      child: const Text('Take Case', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w600)),
                    ),
                  ],
                )
              ],
            )
          ],
        ),
      ),
    );
  }
}

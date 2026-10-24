void CompressionContext::Reset() {
  if (working_memory_ == nullptr) return;
  if (owns_working_memory_) {
    delete working_memory_;
  } else {
    working_memory_->~WorkingMemory();
  }
  working_memory_ = nullptr;
}
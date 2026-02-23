#include "mmap.h"

// Move operators
MappedFragmentIndex::MappedFragmentIndex(MappedFragmentIndex&& other) noexcept : fd_(other.fd_), mapping_(other.mapping_), size_(other.size_), bin_counter_(std::move(other.bin_counter_))
{
    other.fd_ = -1;
    other.mapping_ = MAP_FAILED;
    other.size_ = 0;
}

MappedFragmentIndex& MappedFragmentIndex::operator=(MappedFragmentIndex&& other) noexcept 
{
    if (this != &other) 
    {
        cleanup();
        fd_ = other.fd_;
        mapping_ = other.mapping_;
        size_ = other.size_;
        bin_counter_ = std::move(other.bin_counter_);
        other.fd_ = -1;
        other.mapping_ = MAP_FAILED;
        other.size_ = 0;
        other.bin_counter_.clear();
    }
    return *this;
}

MappedFragmentIndex::MappedFragmentIndex(const std::string& path)
{
    /*
        Read in bin counter file
    */ 
    std::string count_string = path.substr(0, path.size()-4) + "_count.bin";

    // Open at end of file to get size
    std::ifstream f(count_string, std::ios::binary | std::ios::ate);

    if (!f)
    {
        throw std::system_error(errno, std::generic_category(), "Failed to open count file: " + count_string);
    }

    // Get file size
    const auto file_size = f.tellg();
    bin_counter_.resize(static_cast<size_t>(file_size) / sizeof(uint32_t));
    // Go to beginning
    f.seekg(0);

    if(!f.read(reinterpret_cast<char*>(bin_counter_.data()), file_size))
    {
        throw std::system_error(errno, std::generic_category(), "Failed to read count file: " + count_string);
    }

    /*
        MMap magic
     */
    // Open file and get file size 
    fd_ = open(path.c_str(), O_RDONLY);
    if (fd_ == -1)
    {
        throw std::system_error(errno, std::generic_category(), "Failed to open file: " + path);
    }

    struct stat sb;
    if (fstat(fd_, &sb) == -1)
    {
        close(fd_);
        throw std::system_error(errno, std::generic_category(), "Failed to stat file: " + path);
    }

    if (sb.st_size == 0)
    {
        size_ = 0;
        mapping_ = nullptr;
        return;
    }

    size_ = sb.st_size;

    // Open memory mapping, private and read only
    mapping_ = mmap(NULL, size_, PROT_READ, MAP_PRIVATE, fd_, 0);
    if (mapping_ == MAP_FAILED)
    {
        close(fd_);
        throw std::system_error(errno, std::generic_category(), "mmap failed for file: " + path);
    }
    close(fd_); 
    
    data_ = static_cast<const char*>(mapping_); 
}
#include <gtest/gtest.h>
#include <gmock/gmock.h>

class pv_class
{
public:
    virtual std::string name() const = 0;
};

class mock_pv
{
public:
    MOCK_CONST_METHOD0(name, std::string());
};

TEST(gtest_test, google_test_assert)
{
    mock_pv mock;
    ASSERT_EQ(mock.name(), "");
}
import { render, screen, fireEvent } from '@testing-library/react'
import { ChakraProvider } from '@chakra-ui/react'
import { Button } from '@chakra-ui/react'

const renderWithChakra = (component: React.ReactElement) => {
  return render(<ChakraProvider>{component}</ChakraProvider>)
}

describe('Button Component', () => {
  it('renders correctly', () => {
    renderWithChakra(<Button>Test Button</Button>)
    expect(screen.getByRole('button', { name: /test button/i })).toBeInTheDocument()
  })

  it('handles click events', () => {
    const handleClick = jest.fn()
    renderWithChakra(<Button onClick={handleClick}>Click me</Button>)
    
    fireEvent.click(screen.getByRole('button', { name: /click me/i }))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('can be disabled', () => {
    renderWithChakra(<Button isDisabled>Disabled Button</Button>)
    expect(screen.getByRole('button', { name: /disabled button/i })).toBeDisabled()
  })
})
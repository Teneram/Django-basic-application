from typing import Any, Callable, Optional

from django.http import HttpRequest
from django.shortcuts import redirect

# def user_not_authenticated(function=None, redirect_url='/users'):


def user_not_authenticated(
    function: Optional[Callable[..., Any]] = None, redirect_url: str = "/users"
) -> Callable[..., Any]:
    """
    Decorator for views that checks that the user is NOT logged in, redirecting
    to the homepage if necessary by default.
    """

    def decorator(view_func: Callable[..., Any]) -> Callable[..., Any]:
        def _wrapped_view(request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
            if request.user.is_authenticated:
                return redirect(redirect_url)

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    if function:
        return decorator(function)

    return decorator

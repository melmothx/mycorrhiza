<script>
 export default {
     props: [],
 }
</script>
<template>
  <div class="mcrz-plain-box p-1 mt-2 text-sm">
    <p>
      {{ $gettext('You can search by title with the prefix “title:”, by author with the prefix “author:”. Do not add whitespace between the prefix and the term. You can combine the terms with AND, OR, NOT. You can use the asterisk as wildcard. You can quote phrases with double quotes.') }}
    </p>
    <p>
      {{ $gettext('For example:') }}
      <code>title:test OR author:doe* OR "my phrase"</code>
    </p>
  </div>
</template>

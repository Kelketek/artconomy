<template>
  <object style="width:100%;min-height:500px;">
    <param name="movie" :value="asset.file.full">
    <param name="wmode" value="direct">
    <param name="bgcolor" value="#303030">
    <embed :src="asset.file.full" style="width:100%;min-height:500px;" bgcolor="#303030" wmode="direct" />
  </object>
</template>

<script>
  export default {
    name: 'ac-flash-player',
    props: ['asset']
  }
</script>
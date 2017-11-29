<template>
    <div class="character-gallery-image-container">
      <router-link :to="{name: 'Submission', params: {assetID: asset.id}}">
        <div class="character-gallery-image shadowed">
          <img :src="asset.file">
          <div class="gallery-image-overlay">
            <div class="gallery-image-stats"><i class="fa fa-star"></i> {{ asset.favorite_count }} <i class="fa fa-comment"></i> {{ asset.comment_count }}</div>
          </div>
        </div>
        <div class="character-gallery-title text-center">{{ asset.title }}</div>
      </router-link>
    </div>
</template>

<script>
  export default {
    name: 'ac-gallery-preview',
    props: ['asset']
  }
</script>

<style>
  .character-gallery-image {
    height: 15rem;
    overflow: hidden;
    margin-bottom: .25rem;
    position: relative;
  }
  .character-gallery-image img {
    max-width: 100%;
    width: 100%;
    min-height: 100%;
    object-fit: cover;
    position: relative;
    z-index: 2;
  }

  .character-gallery-title {
    font-weight: bold;
    margin-bottom: .5rem;
  }
  .gallery-image-overlay {
    position: absolute;
    top: 0;
    height: 15rem;
    width: 100%;
    z-index: 3;
    opacity: 0;
  }
  .gallery-image-overlay:hover {
    position: absolute;
    top: 0;
    height: 15rem;
    width: 100%;
    z-index: 3;
    opacity: 1;
    background: linear-gradient(to bottom,  rgba(137,255,241,0) 0%,rgba(0,0,0,.6) 100%);
    transition: opacity.5s;
  }
  .gallery-image-stats {
    position: absolute;
    bottom: 1rem;
    right: 3rem;
    color: #fff;
    font-size: 2rem;
  }
</style>